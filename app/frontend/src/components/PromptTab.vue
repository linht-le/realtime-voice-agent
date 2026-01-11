<template>
  <div class="prompt-tab">
    <div class="prompt-header">
      <h2>System Instructions</h2>
    </div>

    <div class="prompt-body">
      <div class="prompt-editor">
        <textarea
          v-model="localPrompt"
          placeholder="Enter system instructions for the AI assistant..."
          @input="hasChanges = true"
        ></textarea>
        <div class="char-count">{{ localPrompt.length }} characters</div>
      </div>

      <div class="prompt-actions">
        <button class="btn-save" @click="savePrompt" :disabled="!hasChanges">
          Save
        </button>
        <button class="btn-reset-default" @click="handleResetToDefault">
          Reset
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usePrompts } from '../composables/usePrompts'

const { prompt, defaultPrompt, updatePrompt, resetToDefault } = usePrompts()
const localPrompt = ref('')
const hasChanges = ref(false)

watch(
  prompt,
  (newValue) => {
    localPrompt.value = newValue || ''
    hasChanges.value = false
  },
  { immediate: true }
)

const savePrompt = async () => {
  const success = await updatePrompt(localPrompt.value)
  if (success) {
    hasChanges.value = false
  }
}

const handleResetToDefault = async () => {
  await resetToDefault()
  hasChanges.value = false
}
</script>

<style scoped>
.prompt-tab {
  height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.prompt-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.prompt-header h2 {
  margin: 0;
  font-size: 18px;
}

.prompt-body {
  padding: 24px;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 16px;
  overflow: hidden;
}

.prompt-editor {
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  overflow: hidden;
}

.prompt-editor textarea {
  width: 100%;
  background: transparent;
  border: none;
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  outline: none;
  overflow-y: auto;
}

.prompt-editor textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.char-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  text-align: right;
}

.prompt-actions {
  display: flex;
  gap: 12px;
}

.prompt-actions button {
  flex: 1;
  height: 48px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save {
  background: #AB47BC;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #9C27B0;
  transform: translateY(-1px);
}

.btn-save:disabled {
  background: rgba(171, 71, 188, 0.3);
  cursor: not-allowed;
}

.btn-reset-default {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.btn-reset-default:hover {
  background: rgba(255, 152, 0, 0.3);
  color: #ff9800;
  border-color: rgba(255, 152, 0, 0.5);
  transform: translateY(-1px);
}

.prompt-editor textarea::-webkit-scrollbar {
  width: 6px;
}

.prompt-editor textarea::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>
