import { ref, computed, watch } from 'vue'
import zh from '../locales/zh.json'
import en from '../locales/en.json'

const messages = { zh, en }
const currentLang = ref(localStorage.getItem('lang') || 'zh')

watch(currentLang, (val) => {
  localStorage.setItem('lang', val)
})

export function useI18n() {
  const t = (key) => {
    const parts = key.split('.')
    let result = messages[currentLang.value]
    for (const p of parts) {
      if (result == null) return key
      result = result[p]
    }
    return result ?? key
  }

  // Support {param} interpolation
  const tf = (key, params = {}) => {
    let str = t(key)
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(`{${k}}`, v)
    }
    return str
  }

  const lang = computed(() => currentLang.value)

  const toggleLang = () => {
    currentLang.value = currentLang.value === 'zh' ? 'en' : 'zh'
  }

  const setLang = (val) => {
    if (messages[val]) currentLang.value = val
  }

  return { t, tf, lang, toggleLang, setLang }
}
