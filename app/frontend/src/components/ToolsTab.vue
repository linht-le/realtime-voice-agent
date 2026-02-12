<template>
  <div class="tools-tab">
    <!-- Header -->
    <header class="tab-header">
      <div class="header-content">
        <h2>Tools</h2>
        <p class="header-subtitle">Configure and manage AI assistant capabilities</p>
      </div>
      <div class="header-badge">
        <span class="badge-count">{{ enabledCount }}</span>
        <span class="badge-label">Active</span>
      </div>
    </header>

    <!-- Body -->
    <div class="tab-body">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading tools...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <AlertCircle :size="48" />
        <h3>Failed to load tools</h3>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="fetchTools">
          <RefreshCw :size="18" />
          Retry
        </button>
      </div>

      <!-- Tools Grid -->
      <div v-else class="tools-grid">
        <TransitionGroup name="card">
          <ToolCard
            v-for="tool in tools"
            :key="tool.name"
            :name="tool.name"
            :tool="tool"
            @toggle="handleToggle"
            @updateDescription="handleUpdateDescription"
            @resetDescription="handleResetDescription"
          />
        </TransitionGroup>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useTools } from '../composables/useTools'
import ToolCard from './ToolCard.vue'

const {
  tools,
  loading,
  error,
  fetchTools,
  toggleTool,
  updateDescription,
  resetDescription,
} = useTools()

const enabledCount = computed(() => {
  return tools.value.filter(t => t.enabled !== false).length
})

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
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* Header */
.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-sm) var(--space-lg);
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.15), rgba(159, 122, 234, 0.08));
  border: 1px solid rgba(177, 156, 217, 0.2);
  border-radius: var(--radius-lg);
}

.badge-count {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
}

.badge-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Body */
.tab-body {
  flex: 1;
  padding: var(--space-xl);
  overflow-y: auto;
}

/* Loading State */
.loading-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-default);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

/* Error State */
.error-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  text-align: center;
  color: var(--color-error);
}

.error-state h3 {
  margin: 0;
  color: var(--text-primary);
}

.error-state p {
  color: var(--text-muted);
  max-width: 400px;
}

.error-state .btn {
  margin-top: var(--space-md);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  border-radius: var(--radius-full);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.error-state .btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--glow-primary-strong);
}

/* Tools Grid */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-lg);
}

/* Card Transitions */
.card-enter-active,
.card-leave-active {
  transition: all 0.4s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.card-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>
