<template>
  <div class="model-switcher" ref="root">
    <button class="model-trigger" :aria-expanded="open" @click="toggle">
      {{ t('model.label') }}:
      <bdi>{{ llmProvider === 'deepseek' ? 'DeepSeek V4.1 Flash' : llmProviders.default_model || t('model.default') }}</bdi>
      <span aria-hidden="true">{{ open ? '▲' : '▼' }}</span>
    </button>
    <div v-if="open" class="model-menu">
      <button class="model-option" :aria-pressed="llmProvider === 'default'" @click="choose('default')">
        {{ t('model.default') }} <bdi>{{ llmProviders.default_model }}</bdi>
      </button>
      <button class="model-option" :aria-pressed="llmProvider === 'deepseek'"
        :disabled="!llmProviders.deepseek_configured" @click="choose('deepseek')">
        <bdi>DeepSeek V4.1 Flash</bdi>
      </button>
      <p class="model-note">{{ t('model.newWork') }}</p>
      <p v-if="!llmProviders.deepseek_configured" class="model-note">
        {{ t('model.addKey') }} <code dir="ltr">DEEPSEEK_API_KEY</code>.
        <a href="https://github.com/settings/codespaces" target="_blank" rel="noopener noreferrer">{{ t('model.secrets') }}</a>
        {{ t('model.restart') }}
      </p>
      <p v-if="error" class="model-error" role="alert">{{ t('model.loadError') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import service from '../api'
import { llmProvider, llmProviders, restoreLLMProvider, selectLLMProvider } from '../store/llmProvider'

const { t } = useI18n()
const open = ref(false)
const root = ref(null)
const error = ref(false)

async function loadProviders() {
  try {
    const response = await service.get('/api/llm/providers')
    restoreLLMProvider(response.data)
    error.value = false
  } catch {
    error.value = true
  }
}
function toggle() {
  open.value = !open.value
  if (open.value) loadProviders()
}
function choose(provider) {
  selectLLMProvider(provider)
  open.value = false
}
function closeOutside(event) {
  if (!root.value?.contains(event.target)) open.value = false
}
onMounted(() => {
  loadProviders()
  document.addEventListener('click', closeOutside)
})
onUnmounted(() => document.removeEventListener('click', closeOutside))
</script>

<style scoped>
.model-switcher { position: relative; font-size: 12px; }
.model-trigger { display: flex; align-items: center; gap: 6px; padding: 6px 10px; border: 1px solid #ccc; background: transparent; color: inherit; cursor: pointer; font: inherit; }
.model-menu { position: absolute; inset-inline-end: 0; top: calc(100% + 8px); width: 280px; padding: 8px; border: 1px solid #ddd; background: white; color: #222; box-shadow: 0 4px 16px #0002; z-index: 1000; text-align: start; }
.model-option { width: 100%; padding: 10px; border: 0; background: transparent; font: inherit; text-align: start; cursor: pointer; }
.model-option[aria-pressed="true"] { background: #f2f2f2; font-weight: 600; }
.model-option:hover:not(:disabled) { background: #eee; }
.model-option:disabled { opacity: .5; cursor: not-allowed; }
.model-note { margin: 10px; color: #666; font-size: 12px; line-height: 1.6; }
.model-note a { color: #333; }
.model-error { margin: 10px; color: #a32929; }
bdi, code { unicode-bidi: isolate; }
@media (max-width: 600px) { .model-trigger { max-width: 160px; flex-wrap: wrap; } .model-menu { width: 250px; } }
</style>
