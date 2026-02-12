<template>
  <div class="app-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="14" stroke="url(#logo-gradient)" stroke-width="2"/>
              <path d="M16 8v8l6 4" stroke="url(#logo-gradient)" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logo-gradient" x1="0" y1="0" x2="32" y2="32">
                  <stop offset="0%" stop-color="#C4B5FD"/>
                  <stop offset="100%" stop-color="#9F7AEA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="logo-text">Voice Agent</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-btn', { active: currentTab === tab.id }]"
          @click="currentTab = tab.id"
        >
          <span class="nav-icon">
            <component :is="tab.icon" :size="20" />
          </span>
          <span class="nav-label">{{ tab.label }}</span>
          <span v-if="currentTab === tab.id" class="nav-indicator"></span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="status-indicator">
          <span :class="['status-dot', { connected: voiceChat.isConnected.value }]"></span>
          <span class="status-text">{{ voiceChat.isConnected.value ? 'Connected' : 'Disconnected' }}</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <Transition name="fade" mode="out-in">
        <VoiceTab v-if="currentTab === 'voice'" key="voice" />
        <PromptTab v-else-if="currentTab === 'prompt'" key="prompt" />
        <SettingsTab v-else-if="currentTab === 'settings'" key="settings" />
        <ToolsTab v-else-if="currentTab === 'tools'" key="tools" />
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { FileText, Mic, Plug, Settings } from 'lucide-vue-next'
import { onMounted, provide, ref } from 'vue'
import PromptTab from './components/PromptTab.vue'
import SettingsTab from './components/SettingsTab.vue'
import ToolsTab from './components/ToolsTab.vue'
import VoiceTab from './components/VoiceTab.vue'
import { usePrompts } from './composables/usePrompts'
import { useSettings } from './composables/useSettings'
import { useVoiceChat } from './composables/useVoiceChat'

const { settings, initialize: initializeSettings } = useSettings()
const { initialize: initializePrompts } = usePrompts()
const voiceChat = useVoiceChat(settings)

provide('voiceChat', voiceChat)

const currentTab = ref('voice')
const tabs = [
  { id: 'voice', label: 'Voice', icon: Mic },
  { id: 'prompt', label: 'Prompt', icon: FileText },
  { id: 'tools', label: 'Tools', icon: Plug },
  { id: 'settings', label: 'Settings', icon: Settings },
]

onMounted(async () => {
  await Promise.all([initializeSettings(), initializePrompts()])
})
</script>

<style scoped>
.app-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--bg-primary);
}

/* Sidebar */
.sidebar {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg, rgba(177, 156, 217, 0.08) 0%, transparent 100%);
  pointer-events: none;
}

.sidebar-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-default);
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.2), rgba(159, 122, 234, 0.1));
  border-radius: var(--radius-md);
  box-shadow: var(--glow-primary);
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: 700;
  background: linear-gradient(135deg, #C4B5FD 0%, #9F7AEA 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  text-align: left;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.15), rgba(159, 122, 234, 0.05));
  opacity: 0;
  transition: opacity var(--transition-normal);
  border-radius: inherit;
}

.nav-btn:hover {
  color: var(--text-secondary);
}

.nav-btn:hover::before {
  opacity: 1;
}

.nav-btn.active {
  color: var(--color-primary);
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.15), rgba(159, 122, 234, 0.08));
  box-shadow: var(--glow-primary);
}

.nav-btn.active::before {
  opacity: 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  position: relative;
  z-index: 1;
}

.nav-label {
  position: relative;
  z-index: 1;
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: linear-gradient(180deg, var(--color-primary-light), var(--color-primary-dark));
  border-radius: 0 var(--radius-full) var(--radius-full) 0;
  box-shadow: var(--glow-primary);
}

.sidebar-footer {
  padding: var(--space-lg);
  border-top: 1px solid var(--border-default);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-glass);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-error);
  transition: all var(--transition-normal);
}

.status-dot.connected {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
}

.status-text {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  font-weight: 500;
}

/* Main Content */
.main-content {
  background: var(--bg-primary);
  overflow: hidden;
  position: relative;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
