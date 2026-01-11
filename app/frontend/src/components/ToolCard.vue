<template>
  <div class="tool-card">
    <div class="card-header">
      <div class="card-title">
        <component :is="getIcon()" :size="24" class="icon" />
        <h3>{{ getTitle() }}</h3>
      </div>
      <label class="toggle">
        <input
          type="checkbox"
          :checked="tool?.enabled ?? true"
          @change="handleToggle"
        />
        <span class="slider"></span>
      </label>
    </div>

    <div class="card-body">
      <div class="status-row">
        <span class="status-label">Status:</span>
        <span :class="['status-badge', getStatusClass()]">
          {{ getStatusText() }}
        </span>
      </div>

      <div class="description-section">
        <div v-if="!isEditing" class="description-view">
          <p class="description-text">{{ tool?.description || 'No description' }}</p>
          <div class="button-group">
            <button @click="startEdit" class="edit-btn" title="Edit description">
              Edit
            </button>
            <button @click="resetToDefault" class="reset-btn" title="Reset to default">
              Reset
            </button>
          </div>
        </div>

        <div v-else class="description-edit">
          <textarea
            v-model="editedDescription"
            class="description-input"
            rows="4"
            placeholder="Enter tool description..."
          ></textarea>
          <div class="edit-actions">
            <button @click="saveDescription" class="save-btn">Save</button>
            <button @click="cancelEdit" class="cancel-btn">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, FileText, FolderOpen } from 'lucide-vue-next'

const props = defineProps({
  name: String,
  tool: Object,
})

const isEditing = ref(false)
const editedDescription = ref('')

const emit = defineEmits(['toggle', 'updateDescription', 'resetDescription'])

const handleToggle = (event) => {
  emit('toggle', { name: props.name, enabled: event.target.checked })
}

const startEdit = () => {
  editedDescription.value = props.tool?.description || ''
  isEditing.value = true
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
    qdrant: 'Document Search (Qdrant)',
    search_in_file: 'Search in File',
    read_file: 'Read File',
    search_files: 'Search Files',
    list_directory: 'List Directory',
  }
  return titles[props.name] || props.name
}

const getStatusClass = () => {
  const enabled = props.tool?.enabled ?? true
  return enabled ? 'active' : 'inactive'
}

const getStatusText = () => {
  const enabled = props.tool?.enabled ?? true
  return enabled ? 'Enabled' : 'Disabled'
}
</script>

<style scoped>
.tool-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon {
  color: #AB47BC;
  flex-shrink: 0;
}

.card-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.toggle {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  border-radius: 24px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .slider {
  background-color: #AB47BC;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

input:disabled + .slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(171, 71, 188, 0.2);
  color: #AB47BC;
}

.status-badge.inactive {
  background: rgba(158, 158, 158, 0.2);
  color: #9e9e9e;
}

.description-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.description-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.description-text {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  white-space: pre-wrap;
}

.button-group {
  display: flex;
  gap: 8px;
}

.edit-btn,
.reset-btn {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn {
  background: rgba(171, 71, 188, 0.2);
  color: #AB47BC;
  border-color: rgba(171, 71, 188, 0.3);
}

.edit-btn:hover {
  background: rgba(171, 71, 188, 0.3);
  border-color: rgba(171, 71, 188, 0.5);
}

.reset-btn {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border-color: rgba(255, 152, 0, 0.3);
}

.reset-btn:hover {
  background: rgba(255, 152, 0, 0.3);
  border-color: rgba(255, 152, 0, 0.5);
}

.description-edit {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.description-input {
  width: 100%;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
}

.description-input:focus {
  outline: none;
  border-color: #AB47BC;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.save-btn,
.cancel-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn {
  background: #AB47BC;
  color: white;
}

.save-btn:hover {
  background: #9c3fad;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
