<template>
  <div class="voice-tab">
    <!-- Header -->
    <header class="tab-header">
      <div class="header-content">
        <h2>Voice Control</h2>
        <p class="header-subtitle">Start a conversation with your AI assistant</p>
      </div>
    </header>

    <!-- Body -->
    <div class="tab-body">
      <!-- Control Button -->
      <div class="control-section">
        <button
          :class="['voice-btn', connectionState]"
          @click="isConnected ? disconnect() : connect()"
          :disabled="connectionState === 'connecting'"
        >
          <span class="btn-icon">
            <Mic v-if="!isConnected" :size="24" />
            <MicOff v-else :size="24" />
          </span>
          <span class="btn-text">
            {{ connectionState === 'connecting' ? 'Connecting...' : isConnected ? 'Stop Conversation' : 'Start Conversation' }}
          </span>
          <span class="btn-glow"></span>
        </button>

        <!-- Error Message -->
        <Transition name="slide-fade">
          <div v-if="connectionError" class="error-message">
            <AlertCircle :size="18" />
            <span>{{ connectionError }}</span>
          </div>
        </Transition>
      </div>

      <!-- Transcripts -->
      <div class="transcripts-section">
        <div class="transcripts-container" ref="transcriptsRef">
          <!-- Empty State -->
          <div v-if="transcripts.length === 0" class="empty-state">
            <div class="empty-icon">
              <Mic :size="48" />
            </div>
            <h3>Ready to Listen</h3>
            <p>Click the button above to start your conversation</p>
          </div>

          <!-- Hidden Transcripts -->
          <div v-else-if="!showTranscripts" class="empty-state">
            <div class="empty-icon">
              <EyeOff :size="48" />
            </div>
            <h3>Transcripts Hidden</h3>
            <p>Enable transcripts in settings to see the conversation</p>
          </div>

          <!-- Messages -->
          <div v-else class="messages-list">
            <TransitionGroup name="message">
              <div
                v-for="(t, index) in transcripts"
                :key="t.id"
                :class="['message-item', t.type]"
              >
                <!-- Avatar -->
                <div class="message-avatar">
                  <User v-if="t.type === 'user'" :size="18" />
                  <Bot v-else :size="18" />
                </div>

                <!-- Bubble -->
                <div class="message-content">
                  <div class="message-meta">
                    <span class="message-sender">{{ t.type === 'user' ? 'You' : 'Assistant' }}</span>
                    <span v-if="showTimestamps && t.timestamp && !t.isPending" class="message-time">
                      {{ formatTime(t.timestamp) }}
                    </span>
                    <span v-if="t.type === 'ai' && getResponseTime(index)" class="response-badge">
                      {{ getResponseTime(index) }}
                    </span>
                  </div>
                  <div class="message-bubble">
                    <p class="message-text">{{ t.text }}</p>
                    <div v-if="t.toolsUsed?.length" class="tools-used">
                      <span
                        v-for="tool in t.toolsUsed"
                        :key="tool"
                        class="tool-chip"
                        :title="getToolLabel(tool)"
                      >
                        <component :is="getToolIcon(tool)" :size="12" />
                        {{ getToolLabel(tool) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </TransitionGroup>

            <!-- Thinking Indicator -->
            <Transition name="slide-fade">
              <div v-if="isAiThinking" class="message-item ai thinking">
                <div class="message-avatar">
                  <Bot :size="18" />
                </div>
                <div class="message-content">
                  <div class="message-bubble">
                    <div class="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, Bot, EyeOff, FileText, FolderOpen, Mic, MicOff, Search, User } from 'lucide-vue-next'
import { computed, inject, nextTick, ref, watch } from 'vue'
import { useSettings } from '../composables/useSettings'

const voiceChat = inject('voiceChat')
const { isConnected, connectionState, connectionError, transcripts, isAiThinking, connect, disconnect } = voiceChat

const { settings } = useSettings()
const transcriptsRef = ref(null)

const showTimestamps = computed(() => {
  const setting = settings.value?.client?.ui?.show_timestamps
  return typeof setting === 'object' ? setting.value : setting ?? true
})

const showTranscripts = computed(() => {
  const setting = settings.value?.client?.ui?.show_transcripts
  return typeof setting === 'object' ? setting.value : setting ?? true
})

// Auto-scroll to bottom
watch(transcripts, async () => {
  await nextTick()
  if (transcriptsRef.value) {
    transcriptsRef.value.scrollTop = transcriptsRef.value.scrollHeight
  }
}, { deep: true })

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const getResponseTime = (index) => {
  const currentMsg = transcripts.value[index]
  if (!currentMsg || currentMsg.type !== 'ai' || currentMsg.responseTimeMs == null) return null
  return `${currentMsg.responseTimeMs}ms`
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
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* Header */
.tab-header {
  padding: var(--space-xl) var(--space-xl) var(--space-lg);
  border-bottom: 1px solid var(--border-default);
  background: linear-gradient(180deg, rgba(177, 156, 217, 0.05) 0%, transparent 100%);
}

.header-content h2 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-xl);
  font-weight: 700;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--color-primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

/* Body */
.tab-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-xl);
  gap: var(--space-xl);
  overflow: hidden;
}

/* Control Section */
.control-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.voice-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  height: 64px;
  padding: 0 var(--space-xl);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  border-radius: var(--radius-full);
  color: white;
  font-size: var(--font-size-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  overflow: hidden;
  box-shadow: var(--glow-primary-strong);
}

.voice-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 40px rgba(177, 156, 217, 0.5);
}

.voice-btn:active:not(:disabled) {
  transform: translateY(0);
}

.voice-btn.connecting {
  background: linear-gradient(135deg, var(--color-warning) 0%, #F59E0B 100%);
  box-shadow: 0 0 30px rgba(251, 191, 36, 0.4);
}

.voice-btn.connected {
  background: linear-gradient(135deg, var(--color-error) 0%, #DC2626 100%);
  box-shadow: 0 0 30px rgba(248, 113, 113, 0.4);
}

.voice-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%);
  pointer-events: none;
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: var(--radius-lg);
  color: var(--color-error);
  font-size: var(--font-size-sm);
}

/* Transcripts Section */
.transcripts-section {
  flex: 1;
  min-height: 0;
  background: var(--bg-glass);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
  backdrop-filter: blur(12px);
}

.transcripts-container {
  height: 100%;
  padding: var(--space-lg);
  overflow-y: auto;
}

/* Empty State */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: var(--space-md);
}

.empty-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.2), rgba(159, 122, 234, 0.1));
  border-radius: 50%;
  color: var(--color-primary);
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(177, 156, 217, 0.2);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 40px rgba(177, 156, 217, 0.4);
    transform: scale(1.05);
  }
}

.empty-state h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

/* Messages List */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.message-item {
  display: flex;
  gap: var(--space-md);
  animation: fadeSlideIn 0.3s ease;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-normal);
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  box-shadow: var(--glow-primary);
}

.message-item.ai .message-avatar {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
}

.message-content {
  flex: 1;
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 0 var(--space-sm);
}

.message-item.user .message-meta {
  flex-direction: row-reverse;
}

.message-sender {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--text-hint);
}

.response-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.2);
  border-radius: var(--radius-full);
  color: #A5B4FC;
  font-weight: 500;
}

.message-bubble {
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(8px);
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  border-radius: var(--radius-lg) var(--radius-lg) var(--space-xs) var(--radius-lg);
  box-shadow: var(--glow-primary);
}

.message-item.ai .message-bubble {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1));
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: var(--text-primary);
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--space-xs);
}

.message-text {
  margin: 0;
  font-size: var(--font-size-base);
  line-height: 1.6;
  word-wrap: break-word;
}

.tools-used {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.tool-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* Typing Indicator */
.message-item.thinking .message-bubble {
  padding: var(--space-md) var(--space-lg);
}

.typing-dots {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 20px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: var(--color-primary-light);
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.message-enter-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>
