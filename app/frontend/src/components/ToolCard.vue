<template>
  <div :class="['tool-card', { disabled: !(tool?.enabled ?? true) }]">
    <!-- Card Header -->
    <div class="card-header">
      <div class="card-icon">
        <component :is="getIcon()" :size="24" />
      </div>
      <div class="card-info">
        <h3>{{ getTitle() }}</h3>
        <span :class="['status-badge', getStatusClass()]">
          {{ getStatusText() }}
        </span>
      </div>
      <label class="toggle-switch">
        <input
          type="checkbox"
          :checked="tool?.enabled ?? true"
          @change="handleToggle"
        />
        <span class="toggle-track">
          <span class="toggle-thumb"></span>
        </span>
      </label>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <!-- Description View -->
      <div v-if="!isEditing" class="description-view">
        <p class="description-text">{{ tool?.description || 'No description available' }}</p>
        <div class="action-buttons">
          <button @click="startEdit" class="action-btn edit">
            <Edit3 :size="14" />
            Edit
          </button>
          <button @click="resetToDefault" class="action-btn reset">
            <RotateCcw :size="14" />
            Reset
          </button>
        </div>
      </div>

      <!-- Description Edit -->
      <div v-else class="description-edit">
        <textarea
          v-model="editedDescription"
          class="description-input"
          rows="4"
          placeholder="Enter tool description..."
          ref="textareaRef"
        ></textarea>
        <div class="edit-actions">
          <button @click="cancelEdit" class="action-btn cancel">
            <X :size="14" />
            Cancel
          </button>
          <button @click="saveDescription" class="action-btn save">
            <Check :size="14" />
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, Edit3, FileText, FolderOpen, RotateCcw, Search, X } from 'lucide-vue-next'
import { nextTick, ref } from 'vue'

const props = defineProps({
  name: String,
  tool: Object,
})

const isEditing = ref(false)
const editedDescription = ref('')
const textareaRef = ref(null)

const emit = defineEmits(['toggle', 'updateDescription', 'resetDescription'])

const handleToggle = (event) => {
  emit('toggle', { name: props.name, enabled: event.target.checked })
}

const startEdit = async () => {
  editedDescription.value = props.tool?.description || ''
  isEditing.value = true
  await nextTick()
  textareaRef.value?.focus()
}

const cancelEdit = () => {
  isEditing.value = false
  editedDescription.value = ''
}

const saveDescription = () => {
  emit('updateDescription', { name: props.name, description: editedDescription.value })
  isEditing.value = false
}

const resetToDefault = () => {
  emit('resetDescription', { name: props.name })
}

const getIcon = () => {
  const icons = {
    web_search: Search,
    qdrant: FileText,
    search_in_file: FileText,
    read_file: FileText,
    search_files: FolderOpen,
    list_directory: FolderOpen,
  }
  return icons[props.name] || FileText
}

const getTitle = () => {
  const titles = {
    web_search: 'Web Search',
    qdrant: 'Document Search',
    search_in_file: 'Search in File',
    read_file: 'Read File',
    search_files: 'Search Files',
    list_directory: 'List Directory',
  }
  return titles[props.name] || props.name
}

const getStatusClass = () => {
  return (props.tool?.enabled ?? true) ? 'active' : 'inactive'
}

const getStatusText = () => {
  return (props.tool?.enabled ?? true) ? 'Enabled' : 'Disabled'
}
</script>

<style scoped>
.tool-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  transition: all var(--transition-normal);
  backdrop-filter: blur(12px);
}

.tool-card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--glow-primary);
  transform: translateY(-2px);
}

.tool-card.disabled {
  opacity: 0.6;
}

.tool-card.disabled:hover {
  box-shadow: none;
  transform: none;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.2), rgba(159, 122, 234, 0.1));
  border-radius: var(--radius-lg);
  color: var(--color-primary);
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-info h3 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.2), rgba(16, 185, 129, 0.1));
  color: var(--color-success);
}

.status-badge.inactive {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  width: 52px;
  height: 28px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-track {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.toggle-thumb {
  position: absolute;
  width: 22px;
  height: 22px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: all var(--transition-normal);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked + .toggle-track {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  box-shadow: var(--glow-primary);
}

.toggle-switch input:checked + .toggle-track .toggle-thumb {
  transform: translateX(24px);
}

/* Card Body */
.card-body {
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-default);
}

.description-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.description-text {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.action-buttons {
  display: flex;
  gap: var(--space-sm);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.action-btn.edit {
  color: var(--color-primary);
  border-color: rgba(177, 156, 217, 0.3);
}

.action-btn.edit:hover {
  background: rgba(177, 156, 217, 0.1);
  border-color: var(--color-primary);
}

.action-btn.reset {
  color: var(--color-warning);
  border-color: rgba(251, 191, 36, 0.3);
}

.action-btn.reset:hover {
  background: rgba(251, 191, 36, 0.1);
  border-color: var(--color-warning);
}

/* Description Edit */
.description-edit {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.description-input {
  width: 100%;
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: inherit;
  font-size: var(--font-size-sm);
  line-height: 1.6;
  resize: vertical;
  transition: all var(--transition-normal);
}

.description-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--glow-primary);
}

.edit-actions {
  display: flex;
  gap: var(--space-sm);
  justify-content: flex-end;
}

.action-btn.cancel {
  color: var(--text-muted);
}

.action-btn.cancel:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.action-btn.save {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-color: transparent;
  color: white;
}

.action-btn.save:hover {
  box-shadow: var(--glow-primary);
  transform: translateY(-1px);
}
</style>
