<template>
  <div class="app-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h1>Voice Assistant</h1>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-button', { active: currentTab === tab.id }]"
          @click="currentTab = tab.id"
        >
          <component :is="tab.icon" :size="20" />
          <span>{{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <div class="main-content">
      <VoiceTab v-if="currentTab === 'voice'" />
      <PromptTab v-else-if="currentTab === 'prompt'" />
      <SettingsTab v-else-if="currentTab === 'settings'" />
      <ToolsTab v-else-if="currentTab === 'tools'" />
    </div>
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
}

.sidebar {
  background: #1a1a1a;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.sidebar-nav {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.nav-button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.nav-button.active {
  background: rgba(171, 71, 188, 0.15);
  color: #AB47BC;
}

.main-content {
  background: #1a1a1a;
  overflow: hidden;
}
</style>
