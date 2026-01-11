import { ref } from 'vue'

const API_BASE = window.location.origin

const schema = ref(null)
const settings = ref(null)
const loading = ref(false)
const error = ref(null)

export function useSettings() {

  function extractValues(schemaSection) {
    if (!schemaSection || typeof schemaSection !== 'object') return {}

    const result = {}
    for (const [key, item] of Object.entries(schemaSection)) {
      if (item && typeof item === 'object') {
        if ('type' in item) {
          result[key] = item.value !== undefined ? item.value : item.default
        } else {
          result[key] = extractValues(item)
        }
      }
    }
    return result
  }

  function updateLocalSettings(data) {
    schema.value = data
    settings.value = {
      backend: extractValues(data.backend),
      client: extractValues(data.client),
    }
  }

  async function apiCall(method, body = null) {
    loading.value = true
    error.value = null
    try {
      const options = { method }
      if (body) {
        options.headers = { 'Content-Type': 'application/json' }
        options.body = JSON.stringify(body)
      }
      const response = await fetch(`${API_BASE}/settings`, options)
      if (!response.ok) throw new Error(`Settings ${method} failed: ${response.statusText}`)
      const data = await response.json()
      updateLocalSettings(data)
      return true
    } catch (err) {
      error.value = err.message
      console.error(`Settings ${method} error:`, err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchSettings() {
    await apiCall('GET')
  }

  async function updateSettings(updates) {
    return await apiCall('PUT', updates)
  }

  async function resetSettings() {
    return await apiCall('DELETE')
  }

  async function initialize() {
    await fetchSettings()
  }

  return {
    schema,
    settings,
    loading,
    error,
    fetchSettings,
    updateSettings,
    resetSettings,
    initialize,
  }
}
