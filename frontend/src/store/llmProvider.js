import { ref } from 'vue'

// Store only the provider name. API keys belong in server-side secrets.
export const llmProvider = ref(localStorage.getItem('mirofish-llm-provider') === 'deepseek' ? 'deepseek' : 'default')
export const llmProviders = ref({ default_model: '', deepseek_configured: false })

export function restoreLLMProvider(data) {
  llmProviders.value = data
  const saved = localStorage.getItem('mirofish-llm-provider')
  llmProvider.value = saved === 'deepseek' && data.deepseek_configured ? 'deepseek' : 'default'
  if (saved === 'deepseek' && !data.deepseek_configured) localStorage.removeItem('mirofish-llm-provider')
}

export function selectLLMProvider(provider) {
  if (provider !== 'default' && (provider !== 'deepseek' || !llmProviders.value.deepseek_configured)) return
  llmProvider.value = provider
  localStorage.setItem('mirofish-llm-provider', provider)
}
