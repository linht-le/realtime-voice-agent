<template>
  <div class="settings-tab">
    <!-- Header -->
    <header class="tab-header">
      <div class="header-content">
        <h2>Settings</h2>
        <p class="header-subtitle">Configure your voice assistant preferences</p>
      </div>
    </header>

    <!-- Body -->
    <div class="tab-body">
      <!-- Navigation Tabs -->
      <div class="settings-nav">
        <button
          v-for="tab in settingsTabs"
          :key="tab.id"
          :class="['nav-btn', { active: currentSettingsTab === tab.id }]"
          @click="currentSettingsTab = tab.id"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- Settings Content -->
      <div class="settings-content">
        <!-- Backend Settings -->
        <div v-if="currentSettingsTab === 'backend'" class="settings-section">
          <!-- Realtime API Section -->
          <div class="section-card">
            <div class="section-header">
              <div class="section-icon">
                <Zap :size="20" />
              </div>
              <div class="section-info">
                <h3>OpenAI Realtime API</h3>
                <p>Configure real-time voice processing settings</p>
              </div>
            </div>
            <div v-if="realtimeSettings.length === 0" class="empty-section">
              No realtime settings available
            </div>
            <div v-else class="settings-list">
              <div v-for="{ key, config } in realtimeSettings" :key="key" class="setting-row">
                <div class="setting-label">
                  <span class="label-text">{{ formatLabel(key) }}</span>
                  <span v-if="config.note" class="label-note">{{ config.note }}</span>
                </div>
                <div class="setting-control">
                  <input
                    v-if="config.type === 'string'"
                    :type="config.sensitive ? 'password' : 'text'"
                    :value="getValue(key)"
                    @input="setValue(key, $event.target.value)"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <input
                    v-else-if="config.type === 'number'"
                    type="number"
                    :value="getValue(key)"
                    @input="setValue(key, Number($event.target.value))"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <label v-else-if="config.type === 'boolean'" class="checkbox-switch">
                    <input
                      type="checkbox"
                      :checked="getValue(key)"
                      @change="setValue(key, $event.target.checked)"
                    />
                    <span class="switch-track"><span class="switch-thumb"></span></span>
                  </label>
                  <select
                    v-else-if="config.type === 'enum'"
                    :value="getValue(key)"
                    @change="setValue(key, $event.target.value)"
                    class="select-field"
                  >
                    <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Backend Logic Section -->
          <div class="section-card">
            <div class="section-header">
              <div class="section-icon">
                <Server :size="20" />
              </div>
              <div class="section-info">
                <h3>Backend Logic</h3>
                <p>Control backend processing behavior</p>
              </div>
            </div>
            <div v-if="backendLogicSettings.length === 0" class="empty-section">
              No backend logic settings available
            </div>
            <div v-else class="settings-list">
              <div v-for="{ key, config } in backendLogicSettings" :key="key" class="setting-row">
                <div class="setting-label">
                  <span class="label-text">{{ formatLabel(key) }}</span>
                  <span v-if="config.note" class="label-note">{{ config.note }}</span>
                </div>
                <div class="setting-control">
                  <input
                    v-if="config.type === 'string'"
                    :type="config.sensitive ? 'password' : 'text'"
                    :value="getValue(key)"
                    @input="setValue(key, $event.target.value)"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <input
                    v-else-if="config.type === 'number'"
                    type="number"
                    :value="getValue(key)"
                    @input="setValue(key, Number($event.target.value))"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <label v-else-if="config.type === 'boolean'" class="checkbox-switch">
                    <input
                      type="checkbox"
                      :checked="getValue(key)"
                      @change="setValue(key, $event.target.checked)"
                    />
                    <span class="switch-track"><span class="switch-thumb"></span></span>
                  </label>
                  <select
                    v-else-if="config.type === 'enum'"
                    :value="getValue(key)"
                    @change="setValue(key, $event.target.value)"
                    class="select-field"
                  >
                    <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Client Settings -->
        <div v-else-if="currentSettingsTab === 'client'" class="settings-section">
          <div class="section-card">
            <div class="section-header">
              <div class="section-icon">
                <Monitor :size="20" />
              </div>
              <div class="section-info">
                <h3>Client Settings</h3>
                <p>Customize the user interface experience</p>
              </div>
            </div>
            <div v-if="clientSettings.length === 0" class="empty-section">
              No client settings available
            </div>
            <div v-else class="settings-list">
              <div v-for="{ key, config } in clientSettings" :key="key" class="setting-row">
                <div class="setting-label">
                  <span class="label-text">{{ formatLabel(key) }}</span>
                  <span v-if="config.note" class="label-note">{{ config.note }}</span>
                </div>
                <div class="setting-control">
                  <input
                    v-if="config.type === 'string'"
                    :type="config.sensitive ? 'password' : 'text'"
                    :value="getValue(key, 'client')"
                    @input="setValue(key, $event.target.value, 'client')"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <input
                    v-else-if="config.type === 'number'"
                    type="number"
                    :value="getValue(key, 'client')"
                    @input="setValue(key, Number($event.target.value), 'client')"
                    :placeholder="config.default?.toString() || ''"
                    class="input-field"
                  />
                  <label v-else-if="config.type === 'boolean'" class="checkbox-switch">
                    <input
                      type="checkbox"
                      :checked="getValue(key, 'client')"
                      @change="setValue(key, $event.target.checked, 'client')"
                    />
                    <span class="switch-track"><span class="switch-thumb"></span></span>
                  </label>
                  <select
                    v-else-if="config.type === 'enum'"
                    :value="getValue(key, 'client')"
                    @change="setValue(key, $event.target.value, 'client')"
                    class="select-field"
                  >
                    <option v-for="opt in config.values" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-row">
        <button class="btn btn-secondary" @click="handleResetToDefaults">
          <RotateCcw :size="18" />
          <span>Reset All</span>
        </button>
        <button
          class="btn btn-primary"
          @click="saveSettings"
          :disabled="!hasChanges"
        >
          <Save :size="18" />
          <span>Save Changes</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Monitor, RotateCcw, Save, Server, Zap } from 'lucide-vue-next'
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
  { id: 'backend', label: 'Backend', icon: Server },
  { id: 'client', label: 'Client', icon: Monitor },
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

/* Navigation */
.settings-nav {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-xs);
  background: var(--bg-glass);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
  width: fit-content;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.nav-btn:hover {
  color: var(--text-secondary);
}

.nav-btn.active {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  box-shadow: var(--glow-primary);
}

/* Settings Content */
.settings-content {
  flex: 1;
  overflow-y: auto;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* Section Card */
.section-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
  backdrop-filter: blur(12px);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-default);
  background: rgba(255, 255, 255, 0.02);
}

.section-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.2), rgba(159, 122, 234, 0.1));
  border-radius: var(--radius-lg);
  color: var(--color-primary);
}

.section-info h3 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-base);
  font-weight: 600;
}

.section-info p {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.empty-section {
  padding: var(--space-xl);
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

/* Settings List */
.settings-list {
  padding: var(--space-sm);
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.setting-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.setting-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.label-text {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.label-note {
  font-size: var(--font-size-xs);
  color: var(--text-hint);
}

.setting-control {
  flex-shrink: 0;
  min-width: 200px;
}

/* Input Fields */
.input-field,
.select-field {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-normal);
}

.input-field:focus,
.select-field:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(177, 156, 217, 0.1);
}

.input-field::placeholder {
  color: var(--text-hint);
}

.select-field option {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

/* Checkbox Switch */
.checkbox-switch {
  position: relative;
  width: 48px;
  height: 26px;
  display: block;
}

.checkbox-switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.switch-track {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.switch-thumb {
  position: absolute;
  width: 20px;
  height: 20px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: all var(--transition-normal);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.checkbox-switch input:checked + .switch-track {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
}

.checkbox-switch input:checked + .switch-track .switch-thumb {
  transform: translateX(22px);
}

/* Actions */
.actions-row {
  display: flex;
  gap: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-default);
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
