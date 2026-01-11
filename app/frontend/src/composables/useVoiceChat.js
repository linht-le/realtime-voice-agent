import { onUnmounted, ref } from 'vue'

const WS_URL = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws`
const SAMPLE_RATE = 24000

export function useVoiceChat(settings) {
  const isConnected = ref(false)
  const connectionState = ref('disconnected')
  const connectionError = ref(null)
  const transcripts = ref([])
  const isAiThinking = ref(false)
  let ws = null
  let audioContext = null
  let mediaStream = null
  let workletNode = null
  let inputGainNode = null
  let outputGainNode = null
  let audioQueue = []
  let isPlaying = false
  let currentSource = null
  let pendingTranscript = null

  function setTemporaryError(message, duration) {
    const errorPrefix = message.split(':')[0]
    connectionError.value = message
    setTimeout(() => {
      if (connectionError.value?.startsWith(errorPrefix)) {
        connectionError.value = null
      }
    }, duration)
  }

  async function connect() {
    try {
      connectionState.value = 'connecting'
      connectionError.value = null
      transcripts.value = []

      ws = new WebSocket(WS_URL)

      ws.onopen = async () => {
        connectionState.value = 'connected'
        isConnected.value = true
        await startRecording()
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleMessage(data)
      }

      ws.onclose = () => {
        connectionState.value = 'disconnected'
        isConnected.value = false
        stopRecording()
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        connectionState.value = 'error'
        connectionError.value = 'Connection failed'
      }
    } catch (error) {
      console.error('Connection failed:', error)
      connectionState.value = 'error'
      connectionError.value = error.message
      throw error
    }
  }

  function disconnect() {
    if (ws) {
      ws.close()
      ws = null
    }
    stopRecording()
    stopAudio()
    isConnected.value = false
    connectionState.value = 'disconnected'
    connectionError.value = null
  }

  function handleMessage(data) {
    switch (data.type) {
      case 'notification':
        addTranscript(`${data.message}`, 'ai')
        speakNotification(data.message)
        break
      case 'audio_delta':
        if (!isAiThinking.value) {
          isAiThinking.value = true
        }
        playAudio(data.audio)
        break
      case 'user_transcript':
        if (pendingTranscript) {
          pendingTranscript.text = data.text
          pendingTranscript.isPending = false
          pendingTranscript = null
        } else {
          addTranscript(data.text, 'user', data.timestamp)
        }
        break
      case 'transcript_done':
        isAiThinking.value = false
        addTranscript(data.text, 'ai', data.timestamp, data.response_time_ms, data.toolsUsed)
        break
      case 'speech_stopped':
        const allowBargeIn = settings?.value?.client?.interaction?.allow_barge_in
        const bargeInValue = typeof allowBargeIn === 'object'
          ? allowBargeIn.value
          : allowBargeIn ?? true

        if (bargeInValue && isPlaying) {
          stopAudio()
        }

        pendingTranscript = {
          text: 'Transcribing...',
          type: 'user',
          isPending: true,
          timestamp: data.timestamp ? new Date(data.timestamp) : new Date()
        }
        transcripts.value.push(pendingTranscript)
        break
      case 'response_created':
        isAiThinking.value = true
        break
      case 'response_failed':
        isAiThinking.value = false
        setTemporaryError(`Response failed: ${data.error?.message || 'Unknown error'}`, 5000)
        break
      case 'response_cancelled':
        isAiThinking.value = false
        break
      case 'session_error':
        setTemporaryError(`Session error: ${data.error?.message || 'Unknown error'}`, 8000)
        break
      case 'session_expired':
        connectionError.value = data.message || 'Session expired'
        disconnect()
        break
      case 'session_closed':
        connectionError.value = data.message || 'Session closed'
        disconnect()
        break
    }
  }

  function speakNotification(text) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)

      const backendLang = settings?.value?.backend?.language
      const uiLang = typeof backendLang === 'object' ? backendLang.value : backendLang || 'auto'
      const langMap = { vi: 'vi-VN', en: 'en-US', ja: 'ja-JP', auto: 'vi-VN' }
      utterance.lang = langMap[uiLang] || 'vi-VN'
      utterance.rate = 1.0

      window.speechSynthesis.speak(utterance)
    }
  }

  function addTranscript(text, type, timestamp = null, responseTimeMs = null, toolsUsed = null) {
    transcripts.value.push({
      id: Date.now() + Math.random(),
      text,
      type,
      timestamp: timestamp ? new Date(timestamp) : new Date(),
      responseTimeMs,
      toolsUsed: toolsUsed || []
    })
  }

  async function startRecording() {
    try {
      const audioInput = settings?.value?.client?.audio_input || {}

      const noiseReduction = typeof audioInput.noise_reduction === 'object'
        ? audioInput.noise_reduction.value
        : audioInput.noise_reduction || 'near_field'

      const echoCancel = typeof audioInput.echo_cancellation === 'object'
        ? audioInput.echo_cancellation.value
        : audioInput.echo_cancellation ?? true

      const autoGain = typeof audioInput.auto_gain_control === 'object'
        ? audioInput.auto_gain_control.value
        : audioInput.auto_gain_control ?? true

      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: SAMPLE_RATE,
          channelCount: 1,
          echoCancellation: echoCancel,
          noiseSuppression: noiseReduction !== 'off',
          autoGainControl: autoGain
        }
      })

      audioContext = new AudioContext({ sampleRate: SAMPLE_RATE })

      await audioContext.audioWorklet.addModule('/audio-processor.js')

      const source = audioContext.createMediaStreamSource(mediaStream)

      inputGainNode = audioContext.createGain()
      const inputSensitivity = typeof audioInput.input_sensitivity === 'object'
        ? audioInput.input_sensitivity.value
        : audioInput.input_sensitivity ?? 0.7
      inputGainNode.gain.value = inputSensitivity

      workletNode = new AudioWorkletNode(audioContext, 'audio-recorder-processor')

      workletNode.port.onmessage = (event) => {
        if (event.data.type === 'audiodata') {
          const pcm16 = convertToPCM16(event.data.data)
          const base64 = arrayBufferToBase64(pcm16)

          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'audio', audio: base64 }))
          }
        }
      }

      source.connect(inputGainNode)
      inputGainNode.connect(workletNode)
      workletNode.connect(audioContext.destination)
    } catch (error) {
      console.error('Recording failed:', error)
      throw error
    }
  }

  function stopRecording() {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }

    if (workletNode) {
      workletNode.disconnect()
      workletNode = null
    }

    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close()
      audioContext = null
    }
  }

  function playAudio(base64Audio) {
    audioQueue.push(base64Audio)
    if (!isPlaying) processAudioQueue()
  }

  async function processAudioQueue() {
    if (audioQueue.length === 0) {
      isPlaying = false
      return
    }

    isPlaying = true
    const base64Audio = audioQueue.shift()

    const responseDelayMs = settings?.value?.client?.interaction?.response_delay_ms
    const responseDelay = typeof responseDelayMs === 'object'
      ? responseDelayMs.value
      : responseDelayMs ?? 0

    if (responseDelay > 0) {
      await new Promise(resolve => setTimeout(resolve, responseDelay))
    }

    try {
      await playChunk(base64Audio)
    } catch (error) {
      console.error('Playback error:', error)
    }

    processAudioQueue()
  }

  function playChunk(base64Audio) {
    return new Promise((resolve) => {
      try {
        const audioData = atob(base64Audio)
        const pcm16Data = new Int16Array(audioData.length / 2)
        const dataView = new DataView(new ArrayBuffer(audioData.length))

        for (let i = 0; i < audioData.length; i++) {
          dataView.setUint8(i, audioData.charCodeAt(i))
        }

        for (let i = 0; i < pcm16Data.length; i++) {
          pcm16Data[i] = dataView.getInt16(i * 2, true)
        }

        const float32Data = new Float32Array(pcm16Data.length)
        for (let i = 0; i < pcm16Data.length; i++) {
          float32Data[i] = pcm16Data[i] / (pcm16Data[i] < 0 ? 0x8000 : 0x7FFF)
        }

        if (!audioContext || audioContext.state === 'closed') {
          audioContext = new AudioContext({ sampleRate: SAMPLE_RATE })
        }

        const audioOutput = settings?.value?.client?.audio_output || {}

        const audioBuffer = audioContext.createBuffer(1, float32Data.length, SAMPLE_RATE)
        audioBuffer.getChannelData(0).set(float32Data)

        currentSource = audioContext.createBufferSource()
        currentSource.buffer = audioBuffer

        const speakingRate = typeof audioOutput.speaking_rate === 'object'
          ? audioOutput.speaking_rate.value
          : audioOutput.speaking_rate ?? 1.0
        currentSource.playbackRate.value = speakingRate

        outputGainNode = audioContext.createGain()
        const volumeGainDb = typeof audioOutput.volume_gain_db === 'object'
          ? audioOutput.volume_gain_db.value
          : audioOutput.volume_gain_db ?? 0
        const gainValue = Math.pow(10, volumeGainDb / 20)
        outputGainNode.gain.value = gainValue

        currentSource.connect(outputGainNode)
        outputGainNode.connect(audioContext.destination)

        currentSource.onended = () => resolve()
        currentSource.start(0)
      } catch (error) {
        console.error('Play error:', error)
        resolve()
      }
    })
  }

  function stopAudio() {
    audioQueue = []
    isPlaying = false
    if (currentSource) {
      try {
        currentSource.stop()
      } catch (e) {}
      currentSource = null
    }
  }

  function convertToPCM16(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2)
    const view = new DataView(buffer)
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]))
      view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
    }
    return buffer
  }

  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    connectionState,
    connectionError,
    transcripts,
    isAiThinking,
    connect,
    disconnect
  }
}
