import { ref } from 'vue'

const API_BASE = window.location.origin

const prompt = ref('')
const defaultPrompt = ref('')
const loading = ref(false)
const error = ref(null)

export function usePrompts() {
  async function fetchPrompts() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE}/prompts`)
      if (!response.ok) throw new Error(`Failed to fetch prompts: ${response.statusText}`)
      const data = await response.json()
      prompt.value = data.current || ''
      defaultPrompt.value = data.default || ''
    } catch (err) {
      error.value = err.message
      console.error('Error fetching prompts:', err)
    } finally {
      loading.value = false
    }
  }

  async function updatePrompt(newPrompt) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE}/prompts`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: newPrompt }),
      })
      if (!response.ok) throw new Error(`Failed to update prompt: ${response.statusText}`)
      prompt.value = newPrompt
      return true
    } catch (err) {
      error.value = err.message
      console.error('Error updating prompt:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function resetToDefault() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE}/prompts`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error(`Failed to reset prompt: ${response.statusText}`)
      const data = await response.json()
      prompt.value = data.prompt || defaultPrompt.value
      return true
    } catch (err) {
      error.value = err.message
      console.error('Error resetting prompt:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function initialize() {
    await fetchPrompts()
  }

  return {
    prompt,
    defaultPrompt,
    loading,
    error,
    fetchPrompts,
    updatePrompt,
    resetToDefault,
    initialize,
  }
}
