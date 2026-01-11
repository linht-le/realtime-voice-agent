<template>
  <div class="settings-tab">
    <div class="settings-header">
      <h2>Settings</h2>
    </div>

    <div class="settings-body">
      <div class="settings-nav">
        <button
          v-for="tab in settingsTabs"
          :key="tab.id"
          :class="['settings-nav-btn', { active: currentSettingsTab === tab.id }]"
          @click="currentSettingsTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="settings-content">
        <div v-if="currentSettingsTab === 'backend'" class="settings-section">
          <h3>OpenAI Realtime API</h3>
          <div v-if="realtimeSettings.length === 0" class="empty-settings">
            No realtime settings available
          </div>
          <div v-else class="settings-grid">
            <div v-for="{ key, config } in realtimeSettings" :key="key" class="setting-item">
              <label>{{ formatLabel(key) }}</label>
              <input
                v-if="config.type === 'string'"
                :type="config.sensitive ? 'password' : 'text'"
                :value="getValue(key)"
                @input="setValue(key, $event.target.value)"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'number'"
                type="number"
                :value="getValue(key)"
                @input="setValue(key, Number($event.target.value))"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'boolean'"
                type="checkbox"
                :checked="getValue(key)"
                @change="setValue(key, $event.target.checked)"
              />
              <select
                v-else-if="config.type === 'enum'"
                :value="getValue(key)"
                @change="setValue(key, $event.target.value)"
              >
                <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <p class="setting-note" v-if="config.note">{{ config.note }}</p>
            </div>
          </div>

          <h3 style="margin-top: 32px">Backend Logic</h3>
          <div v-if="backendLogicSettings.length === 0" class="empty-settings">
            No backend logic settings available
          </div>
          <div v-else class="settings-grid">
            <div v-for="{ key, config } in backendLogicSettings" :key="key" class="setting-item">
              <label>{{ formatLabel(key) }}</label>
              <input
                v-if="config.type === 'string'"
                :type="config.sensitive ? 'password' : 'text'"
                :value="getValue(key)"
                @input="setValue(key, $event.target.value)"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'number'"
                type="number"
                :value="getValue(key)"
                @input="setValue(key, Number($event.target.value))"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'boolean'"
                type="checkbox"
                :checked="getValue(key)"
                @change="setValue(key, $event.target.checked)"
              />
              <select
                v-else-if="config.type === 'enum'"
                :value="getValue(key)"
                @change="setValue(key, $event.target.value)"
              >
                <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <p class="setting-note" v-if="config.note">{{ config.note }}</p>
            </div>
          </div>
        </div>

        <div v-else-if="currentSettingsTab === 'client'" class="settings-section">
          <h3>Client Settings</h3>
          <div v-if="clientSettings.length === 0" class="empty-settings">
            No client settings available
          </div>
          <div v-else class="settings-grid">
            <div v-for="{ key, config } in clientSettings" :key="key" class="setting-item">
              <label>{{ formatLabel(key) }}</label>
              <input
                v-if="config.type === 'string'"
                :type="config.sensitive ? 'password' : 'text'"
                :value="getValue(key, 'client')"
                @input="setValue(key, $event.target.value, 'client')"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'number'"
                type="number"
                :value="getValue(key, 'client')"
                @input="setValue(key, Number($event.target.value), 'client')"
                :placeholder="config.default?.toString() || ''"
              />
              <input
                v-else-if="config.type === 'boolean'"
                type="checkbox"
                :checked="getValue(key, 'client')"
                @change="setValue(key, $event.target.checked, 'client')"
              />
              <select
                v-else-if="config.type === 'enum'"
                :value="getValue(key, 'client')"
                @change="setValue(key, $event.target.value, 'client')"
              >
                <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <p class="setting-note" v-if="config.note">{{ config.note }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-actions">
        <button class="btn-save" @click="saveSettings" :disabled="!hasChanges">
          Save
        </button>
        <button class="btn-reset-default" @click="handleResetToDefaults">
          Reset
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useSettings } from '../composables/useSettings'

const { settings, schema, updateSettings, resetSettings: resetToDefaults } = useSettings()
const currentSettingsTab = ref('backend')
const hasChanges = ref(false)
const localSettings = ref({
  backend: {},
  client: {},
})

const settingsTabs = [
  { id: 'backend', label: 'Backend' },
  { id: 'client', label: 'Client' },
]

const flattenSettings = (settings, prefix = '') => {
  const result = []
  for (const [key, value] of Object.entries(settings || {})) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (value && typeof value === 'object') {
      if (value.type) {
        result.push({ key: fullKey, config: value })
      } else {
        result.push(...flattenSettings(value, fullKey))
      }
    }
  }
  return result
}

const realtimeSettings = computed(() => {
  if (!schema.value?.backend) return []
  return flattenSettings(schema.value.backend).filter(({ config }) =>
    config.category === 'realtime_native'
  )
})

const backendLogicSettings = computed(() => {
  if (!schema.value?.backend) return []
  return flattenSettings(schema.value.backend).filter(({ config }) =>
    config.category === 'backend_logic'
  )
})

const clientSettings = computed(() => {
  if (!schema.value?.client) return []
  return flattenSettings(schema.value.client)
})

const formatLabel = (key) => {
  return key
    .split(/[._]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const getValue = (key, section = 'backend') => {
  const keys = key.split('.')
  let value = localSettings.value[section]
  for (const k of keys) {
    value = value?.[k]
  }
  return value
}

const setValue = (key, value, section = 'backend') => {
  const keys = key.split('.')
  let target = localSettings.value[section]

  for (let i = 0; i < keys.length - 1; i++) {
    if (!target[keys[i]]) {
      target[keys[i]] = {}
    }
    target = target[keys[i]]
  }

  target[keys[keys.length - 1]] = value
  hasChanges.value = true
}


const saveSettings = async () => {
  await updateSettings(localSettings.value)
  hasChanges.value = false
}

const handleResetToDefaults = async () => {
  await resetToDefaults()
  hasChanges.value = false
}

watch(
  settings,
  (newSettings) => {
    if (!hasChanges.value && newSettings) {
      localSettings.value = {
        backend: JSON.parse(JSON.stringify(newSettings.backend || {})),
        client: JSON.parse(JSON.stringify(newSettings.client || {})),
      }
    }
  },
  { deep: true, immediate: true }
)
</script>

<style scoped>
.settings-tab {
  height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.settings-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-header h2 {
  margin: 0;
  font-size: 18px;
}

.settings-body {
  padding: 24px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 16px;
  overflow: hidden;
}

.settings-nav {
  display: flex;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-nav-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-nav-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.settings-nav-btn.active {
  background: rgba(171, 71, 188, 0.15);
  color: #AB47BC;
}

.settings-content {
  overflow-y: auto;
  padding-right: 8px;
}

.settings-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.settings-grid {
  display: grid;
  gap: 20px;
}

.setting-item {
  display: grid;
  gap: 8px;
}

.setting-item label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.setting-item input,
.setting-item select {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  transition: all 0.2s;
}

.setting-item select option {
  background-color: #1e1e1e;
  color: #fff;
}

.setting-item input:focus,
.setting-item select:focus {
  outline: none;
  border-color: #AB47BC;
  background: rgba(255, 255, 255, 0.08);
}

.setting-item input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.setting-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.4;
}

.setting-note {
  margin: 4px 0 0 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  font-style: italic;
  line-height: 1.3;
}

.empty-settings {
  padding: 32px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}

.settings-actions {
  display: flex;
  gap: 12px;
}

.settings-actions button {
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
}

.settings-content::-webkit-scrollbar {
  width: 6px;
}

.settings-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>
