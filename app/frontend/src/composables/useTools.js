import { ref } from 'vue'

const tools = ref([])
const loading = ref(false)
const error = ref(null)

export function useTools() {
  const fetchTools = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/tools')
      if (!response.ok) throw new Error('Failed to fetch tools')

      tools.value = await response.json()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const toolAction = async (url, method, body, errorMsg) => {
    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || errorMsg)
      }

      await fetchTools()
      return { success: true }
    } catch (e) {
      return { success: false, error: e.message }
    }
  }

  const toggleTool = (name, enabled) =>
    toolAction('/tools/toggle', 'POST', { name, enabled }, 'Failed to toggle tool')

  const updateDescription = (name, description) =>
    toolAction('/tools/description', 'PUT', { name, description }, 'Failed to update description')

  const resetDescription = async (name) => {
    try {
      const response = await fetch(`/tools/description/${name}`, { method: 'DELETE' })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to reset description')
      }

      await fetchTools()
      return { success: true }
    } catch (e) {
      return { success: false, error: e.message }
    }
  }

  return {
    tools,
    loading,
    error,
    fetchTools,
    toggleTool,
    updateDescription,
    resetDescription,
  }
}
