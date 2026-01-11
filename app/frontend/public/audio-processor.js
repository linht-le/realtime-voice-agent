class AudioRecorderProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0]

    if (input && input.length > 0) {
      const channelData = input[0]

      this.port.postMessage({
        type: 'audiodata',
        data: channelData
      })
    }

    return true
  }
}

registerProcessor('audio-recorder-processor', AudioRecorderProcessor)
