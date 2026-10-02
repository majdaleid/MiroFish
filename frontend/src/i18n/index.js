import { createI18n } from 'vue-i18n'
import { watch } from 'vue'
import languages from '../../../locales/languages.json'

const localeFiles = import.meta.glob('../../../locales/!(languages).json', { eager: true })

const messages = {}
const availableLocales = []

for (const path in localeFiles) {
  const key = path.match(/\/([^/]+)\.json$/)[1]
  if (languages[key]) {
    messages[key] = localeFiles[path].default
    availableLocales.push({ key, label: languages[key].label })
  }
}

const storedLocale = localStorage.getItem('locale')
const savedLocale = messages[storedLocale] ? storedLocale : 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages
})

// Apply before mounting and whenever the user changes language, including reloads.
watch(i18n.global.locale, (locale) => {
  document.documentElement.lang = locale
  document.documentElement.dir = languages[locale]?.direction || 'ltr'
  document.title = messages[locale].meta.title
  document.querySelector('meta[name="description"]')?.setAttribute('content', messages[locale].meta.description)
  localStorage.setItem('locale', locale)
}, { immediate: true })

export { availableLocales }
export default i18n
