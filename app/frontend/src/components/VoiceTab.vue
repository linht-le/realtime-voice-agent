<template>
  <div class="voice-tab">
    <div class="voice-header">
      <h2>Voice Control</h2>
    </div>

    <div class="voice-body">
      <button
        :class="['voice-btn', connectionState]"
        @click="isConnected ? disconnect() : connect()"
        :disabled="connectionState === 'connecting'"
      >
        {{ connectionState === 'connecting' ? 'CONNECTING...' : isConnected ? 'STOP' : 'START' }}
      </button>

      <div v-if="connectionError" class="error">
        <AlertCircle :size="16" />
        {{ connectionError }}
      </div>

      <div class="transcripts">
        <div v-if="transcripts.length === 0" class="empty">
          <Mic :size="64" />
          <p>Click START to begin your conversation</p>
        </div>

        <div v-else-if="!showTranscripts" class="empty">
          <Mic :size="64" />
          <p>Transcripts hidden</p>
        </div>

        <div v-else class="messages">
          <div
            v-for="(t, index) in transcripts"
            :key="t.id"
            :class="['message-wrapper', t.type]"
          >
            <div class="avatar-icon">
              <User v-if="t.type === 'user'" :size="20" />
              <Bot v-else :size="20" />
            </div>
            <div class="message-bubble">
              <div class="message-header">
                <div class="header-right">
                  <span v-if="showTimestamps && t.timestamp && !t.isPending" class="time">
                    {{ formatTime(t.timestamp) }}
                  </span>
                  <span
                    v-for="tool in t.toolsUsed"
                    :key="tool"
                    class="tool-badge"
                    :title="getToolLabel(tool)"
                  >
                    <component :is="getToolIcon(tool)" :size="12" />
                  </span>
                  <span v-if="t.type === 'ai' && getResponseTime(index)" class="response-time-badge">
                    {{ getResponseTime(index) }}
                  </span>
                </div>
              </div>
              <div class="message-body">{{ t.text }}</div>
            </div>
          </div>

          <!-- AI Thinking Indicator -->
          <div v-if="isAiThinking" class="message-wrapper ai">
            <div class="avatar-icon">
              <Bot :size="20" />
            </div>
            <div class="message-bubble thinking-bubble">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, Mic, User, Bot, Search, FileText, FolderOpen } from 'lucide-vue-next'
import { computed, inject } from 'vue'
import { useSettings } from '../composables/useSettings'

const voiceChat = inject('voiceChat')
const { isConnected, connectionState, connectionError, transcripts, isAiThinking, connect, disconnect } = voiceChat

const { settings } = useSettings()

const showTimestamps = computed(() => {
  const setting = settings.value?.client?.ui?.show_timestamps
  return typeof setting === 'object' ? setting.value : setting ?? true
})

const showTranscripts = computed(() => {
  const setting = settings.value?.client?.ui?.show_transcripts
  return typeof setting === 'object' ? setting.value : setting ?? true
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

const getResponseTime = (index) => {
  const currentMsg = transcripts.value[index]
  if (!currentMsg || currentMsg.type !== 'ai') {
    return null
  }

  if (currentMsg.responseTimeMs != null) {
    return `${currentMsg.responseTimeMs}ms`
  }

  return null
}

const getToolIcon = (toolName) => {
  const iconMap = {
    'web_search': Search,
    'search_in_file': FileText,
    'read_file': FileText,
    'search_files': FolderOpen,
    'list_directory': FolderOpen,
  }
  return iconMap[toolName] || FileText
}

const getToolLabel = (toolName) => {
  const labelMap = {
    'web_search': 'Web Search',
    'search_in_file': 'Search File',
    'read_file': 'Read File',
    'search_files': 'Find Files',
    'list_directory': 'List Dir',
  }
  return labelMap[toolName] || toolName
}
</script>

<style scoped>
.voice-tab {
  height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.voice-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.voice-header h2 {
  margin: 0;
  font-size: 18px;
}

.voice-body {
  padding: 24px;
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 16px;
  overflow: hidden;
}

.voice-btn {
  height: 60px;
  background: #AB47BC;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.voice-btn:hover:not(:disabled) {
  background: #9C27B0;
  transform: translateY(-2px);
}

.voice-btn.connecting {
  background: #ff9800;
}

.voice-btn.connected {
  background: #ef5350;
}

.voice-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(239, 83, 80, 0.1);
  border: 1px solid rgba(239, 83, 80, 0.3);
  border-radius: 8px;
  color: #ef5350;
}

.transcripts {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  overflow-y: auto;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.5);
  gap: 12px;
}

.empty svg {
  color: #AB47BC;
  opacity: 0.6;
  animation: pulse 2s ease-in-out infinite;
}

.empty p {
  font-size: 14px;
  font-weight: 500;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 4px 0;
}

.message-wrapper {
  display: flex;
  width: 100%;
  gap: 8px;
  align-items: flex-start;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-wrapper.ai {
  flex-direction: row;
}

.avatar-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.message-wrapper.user .avatar-icon {
  background: linear-gradient(135deg, #AB47BC 0%, #BA68C8 100%);
  color: #ffffff;
  border: 2px solid rgba(171, 71, 188, 0.3);
}

.message-wrapper.ai .avatar-icon {
  background: linear-gradient(135deg, #7E57C2 0%, #9575CD 100%);
  color: #ffffff;
  border: 2px solid rgba(126, 87, 194, 0.3);
}

.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 16px;
  word-wrap: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(10px);
}

.message-wrapper.user .message-bubble {
  background: linear-gradient(135deg, #AB47BC 0%, #BA68C8 100%);
  color: #ffffff;
  border: 1px solid rgba(171, 71, 188, 0.4);
}

.message-wrapper.ai .message-bubble {
  background: linear-gradient(135deg, #7E57C2 0%, #9575CD 100%);
  color: #ffffff;
  border: 1px solid rgba(126, 87, 194, 0.4);
}

.message-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time {
  font-size: 10px;
  opacity: 0.8;
  white-space: nowrap;
  font-weight: 500;
}

.tool-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 6px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 5px;
  color: #ffffff;
  backdrop-filter: blur(4px);
  cursor: help;
  transition: all 0.2s ease;
}

.tool-badge:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.response-time-badge {
  font-size: 9px;
  font-weight: 600;
  padding: 3px 7px;
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: #ffffff;
  white-space: nowrap;
  backdrop-filter: blur(4px);
}

.message-body {
  font-size: 14px;
  line-height: 1.6;
  font-weight: 400;
  letter-spacing: 0.01em;
}

.transcripts::-webkit-scrollbar {
  width: 6px;
}

.transcripts::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.thinking-bubble {
  padding: 14px 18px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 20px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}
</style>
