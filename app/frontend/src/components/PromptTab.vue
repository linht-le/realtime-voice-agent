<template>
  <div class="prompt-tab">
    <!-- Header -->
    <header class="tab-header">
      <div class="header-content">
        <h2>System Instructions</h2>
        <p class="header-subtitle">Customize how your AI assistant behaves</p>
      </div>
    </header>

    <!-- Body -->
    <div class="tab-body">
      <!-- Editor Card -->
      <div class="editor-card">
        <div class="editor-header">
          <div class="editor-title">
            <FileText :size="20" />
            <span>System Prompt</span>
          </div>
          <div class="char-counter">
            <span class="char-count">{{ localPrompt.length }}</span>
            <span class="char-label">characters</span>
          </div>
        </div>

        <div class="editor-body">
          <textarea
            v-model="localPrompt"
            placeholder="Enter system instructions for the AI assistant...

Example:
You are a helpful assistant specialized in...
- Always respond in a friendly manner
- Focus on providing accurate information
- Ask clarifying questions when needed"
            @input="hasChanges = true"
          ></textarea>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-row">
        <button class="btn btn-secondary" @click="handleResetToDefault">
          <RotateCcw :size="18" />
          <span>Reset to Default</span>
        </button>
        <button
          class="btn btn-primary"
          @click="savePrompt"
          :disabled="!hasChanges"
          :class="{ saving: isSaving }"
        >
          <Save :size="18" />
          <span>{{ isSaving ? 'Saving...' : 'Save Changes' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FileText, RotateCcw, Save } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { usePrompts } from '../composables/usePrompts'

const { prompt, defaultPrompt, updatePrompt, resetToDefault } = usePrompts()
const localPrompt = ref('')
const hasChanges = ref(false)
const isSaving = ref(false)

watch(
  prompt,
  (newValue) => {
    localPrompt.value = newValue || ''
    hasChanges.value = false
  },
  { immediate: true }
)

const savePrompt = async () => {
  isSaving.value = true
  const success = await updatePrompt(localPrompt.value)
  if (success) {
    hasChanges.value = false
  }
  isSaving.value = false
}

const handleResetToDefault = async () => {
  await resetToDefault()
  hasChanges.value = false
}
</script>

<style scoped>
.prompt-tab {
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
  gap: var(--space-lg);
  overflow: hidden;
}

/* Editor Card */
.editor-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-glass);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
  backdrop-filter: blur(12px);
  transition: all var(--transition-normal);
}

.editor-card:focus-within {
  border-color: var(--border-focus);
  box-shadow: var(--glow-primary);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-default);
  background: rgba(255, 255, 255, 0.02);
}

.editor-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.char-counter {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs);
}

.char-count {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
}

.char-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.editor-body {
  flex: 1;
  padding: var(--space-lg);
  overflow: hidden;
}

.editor-body textarea {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: var(--font-size-sm);
  line-height: 1.7;
  resize: none;
  outline: none;
}

.editor-body textarea::placeholder {
  color: var(--text-hint);
}

/* Actions */
.actions-row {
  display: flex;
  gap: var(--space-md);
}

.btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  height: 52px;
  padding: 0 var(--space-xl);
  border: none;
  border-radius: var(--radius-full);
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  box-shadow: var(--glow-primary);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(177, 156, 217, 0.5);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-primary.saving {
  pointer-events: none;
}

.btn-secondary {
  background: var(--bg-glass);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-hover);
  color: var(--text-primary);
}
</style>
