<template>
  <div class="tools-tab">
    <div class="tools-header">
      <h2>Tools</h2>
      <p class="help-text">Configure tool API keys in .env file, then toggle them here</p>
    </div>

    <div class="tools-body">
      <div v-if="loading" class="loading">Loading tools...</div>

      <div v-else-if="error" class="error">{{ error }}</div>

      <div v-else class="tools-grid">
        <ToolCard
          v-for="tool in tools"
          :key="tool.name"
          :name="tool.name"
          :tool="tool"
          @toggle="handleToggle"
          @updateDescription="handleUpdateDescription"
          @resetDescription="handleResetDescription"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ToolCard from './ToolCard.vue'
import { useTools } from '../composables/useTools'

const {
  tools,
  loading,
  error,
  fetchTools,
  toggleTool,
  updateDescription,
  resetDescription,
} = useTools()

onMounted(async () => {
  await fetchTools()
})

const handleToggle = async ({ name, enabled }) => {
  await toggleTool(name, enabled)
}

const handleUpdateDescription = async ({ name, description }) => {
  await updateDescription(name, description)
}

const handleResetDescription = async ({ name }) => {
  await resetDescription(name)
}
</script>

<style scoped>
.tools-tab {
  height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.tools-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tools-header h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.tools-header .help-text {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.tools-body {
  padding: 24px;
  overflow-y: auto;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.6);
}

.error {
  color: #f44336;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .tools-grid {
    grid-template-columns: 1fr;
  }
}

.tools-body::-webkit-scrollbar {
  width: 6px;
}

.tools-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>
