<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <div>
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white">{{ t('settings.title') }}</h2>
      <p class="text-sm text-gray-400 mt-1">{{ t('settings.subtitle') }}</p>
    </div>

    <!-- 提醒频率 -->
    <section class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">🔔 {{ t('settings.frequency') }}</h3>
      <p class="text-sm text-gray-400 mb-4">{{ t('settings.frequencyDesc') }}</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in freqOptions"
          :key="opt.value"
          type="button"
          @click="togglePreset(opt.value)"
          class="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors"
          :class="presetDays.includes(opt.value)
            ? 'bg-primary-500 border-primary-500 text-white'
            : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300'"
        >
          {{ opt.label }}
        </button>
      </div>
      <div class="mt-4 flex items-center gap-2">
        <label class="text-sm text-gray-500 whitespace-nowrap">{{ t('settings.customDays') }}</label>
        <input
          v-model="extraDaysText"
          type="text"
          :placeholder="t('settings.customDaysPlaceholder')"
          class="flex-1 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm"
        />
      </div>
    </section>

    <!-- Server酱 -->
    <section class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <div class="flex items-center justify-between mb-1">
        <h3 class="text-lg font-bold text-gray-800 dark:text-white">🔔 {{ t('settings.serverchan') }}</h3>
        <button
          type="button"
          @click="form.serverchan_enabled = !form.serverchan_enabled"
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0"
          :class="form.serverchan_enabled ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'"
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
            :class="form.serverchan_enabled ? 'translate-x-6' : 'translate-x-1'"
          />
        </button>
      </div>
      <p class="text-sm text-gray-400 mb-4">{{ t('settings.serverchanDesc') }}</p>
      <label class="text-sm text-gray-500">{{ t('settings.serverchanKey') }}</label>
      <input
        v-model="form.serverchan_sckey"
        type="text"
        :placeholder="t('settings.serverchanKeyPlaceholder')"
        :disabled="!form.serverchan_enabled"
        class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50"
      />
      <p class="text-xs text-gray-400 mt-1">{{ t('settings.serverchanHelp') }}</p>
    </section>

    <!-- 邮件 -->
    <section class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <div class="flex items-center justify-between mb-1">
        <h3 class="text-lg font-bold text-gray-800 dark:text-white">📧 {{ t('settings.email') }}</h3>
        <button
          type="button"
          @click="form.email_enabled = !form.email_enabled"
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0"
          :class="form.email_enabled ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'"
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
            :class="form.email_enabled ? 'translate-x-6' : 'translate-x-1'"
          />
        </button>
      </div>
      <p class="text-sm text-gray-400 mb-4">{{ t('settings.emailDesc') }}</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailHost') }}</label>
          <input v-model="form.email_smtp_host" type="text" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailPort') }}</label>
          <input v-model.number="form.email_smtp_port" type="number" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailUser') }}</label>
          <input v-model="form.email_smtp_user" type="text" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailPassword') }}</label>
          <input v-model="form.email_smtp_password" type="password" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailFrom') }}</label>
          <input v-model="form.email_from_name" type="text" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
        <div>
          <label class="text-sm text-gray-500">{{ t('settings.emailTo') }}</label>
          <input v-model="form.email_to" type="text" :disabled="!form.email_enabled"
            class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm disabled:opacity-50" />
        </div>
      </div>
    </section>

    <!-- 消息模板 -->
    <section class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">📝 {{ t('settings.template') }}</h3>
      <p class="text-sm text-gray-400 mb-2">{{ t('settings.templateDesc') }}</p>
      <div class="flex flex-wrap gap-1.5 mb-3">
        <span
          v-for="v in templateVars"
          :key="v"
          class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-xs text-gray-500 font-mono"
        >{{ v }}</span>
      </div>
      <textarea
        v-model="form.message_template"
        rows="4"
        class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm font-mono"
      />
    </section>

    <!-- 操作按钮 -->
    <div class="flex items-center gap-3 flex-wrap">
      <button
        @click="save"
        :disabled="saving"
        class="px-5 py-2.5 rounded-xl bg-primary-500 hover:bg-primary-600 text-white font-medium transition-colors disabled:opacity-50"
      >
        {{ saving ? t('common.loading') : t('settings.save') }}
      </button>
      <button
        @click="testSend"
        :disabled="testing || !hasChannel"
        class="px-5 py-2.5 rounded-xl border border-primary-500 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 font-medium transition-colors disabled:opacity-50"
      >
        {{ testing ? t('common.loading') : t('settings.testSend') }}
      </button>
      <span v-if="message" class="text-sm" :class="messageType === 'ok' ? 'text-green-500' : 'text-red-500'">
        {{ message }}
      </span>
    </div>

    <!-- 测试结果 -->
    <div
      v-if="testResult"
      class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700"
    >
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-3">{{ t('settings.testResult') }}</h3>
      <div class="flex items-center gap-8">
        <div>
          <div class="text-sm text-gray-400">{{ t('settings.testEmail') }}</div>
          <div :class="testResult.email ? 'text-green-500' : 'text-red-500'" class="font-medium">
            {{ testResult.email ? '✓ ' + t('settings.success') : '✗ ' + t('settings.failed') }}
          </div>
        </div>
        <div>
          <div class="text-sm text-gray-400">{{ t('settings.testServerchan') }}</div>
          <div :class="testResult.serverchan ? 'text-green-500' : 'text-red-500'" class="font-medium">
            {{ testResult.serverchan ? '✓ ' + t('settings.success') : '✗ ' + t('settings.failed') }}
          </div>
        </div>
      </div>
      <p class="text-xs text-gray-400 mt-3">{{ t('settings.testNote') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'

const { t, lang } = useI18n()
const { getSettings, updateSettings, testReminder } = useApi()

const PRESET = [0, 1, 3, 7, 15, 30]

const form = reactive({
  serverchan_enabled: false,
  serverchan_sckey: '',
  email_enabled: false,
  email_smtp_host: 'smtp.gmail.com',
  email_smtp_port: 587,
  email_smtp_user: '',
  email_smtp_password: '',
  email_from_name: '🎂 生日提醒',
  email_to: '',
  message_template: '',
})

const presetDays = ref([])
const extraDaysText = ref('')
const saving = ref(false)
const testing = ref(false)
const message = ref('')
const messageType = ref('ok')
const testResult = ref(null)

const freqOptions = computed(() => [
  { value: 0, label: lang.value === 'zh' ? '当天' : 'Today' },
  { value: 1, label: lang.value === 'zh' ? '提前1天' : '1 day' },
  { value: 3, label: lang.value === 'zh' ? '提前3天' : '3 days' },
  { value: 7, label: lang.value === 'zh' ? '提前7天' : '1 week' },
  { value: 15, label: lang.value === 'zh' ? '提前15天' : '15 days' },
  { value: 30, label: lang.value === 'zh' ? '提前30天' : '1 month' },
])

const templateVars = ['{name}', '{days}', '{date}', '{age}', '{category}']
const hasChannel = computed(() => form.serverchan_enabled || form.email_enabled)

function togglePreset(v) {
  const i = presetDays.value.indexOf(v)
  if (i >= 0) presetDays.value.splice(i, 1)
  else presetDays.value.push(v)
}

function mergedDays() {
  const extra = extraDaysText.value
    .split(',')
    .map((s) => parseInt(s.trim(), 10))
    .filter((n) => !isNaN(n) && n >= 0 && n <= 365 && !PRESET.includes(n))
  return Array.from(new Set([...presetDays.value, ...extra])).sort((a, b) => b - a)
}

function splitDays(arr) {
  presetDays.value = arr.filter((d) => PRESET.includes(d))
  extraDaysText.value = arr.filter((d) => !PRESET.includes(d)).join(', ')
}

async function load() {
  try {
    const s = await getSettings()
    Object.assign(form, s)
    splitDays(s.remind_ahead_days || [])
  } catch (e) {
    console.error('load settings failed:', e)
  }
}

async function persist() {
  return updateSettings({
    serverchan_enabled: form.serverchan_enabled,
    serverchan_sckey: form.serverchan_sckey,
    email_enabled: form.email_enabled,
    email_smtp_host: form.email_smtp_host,
    email_smtp_port: form.email_smtp_port,
    email_smtp_user: form.email_smtp_user,
    email_smtp_password: form.email_smtp_password,
    email_from_name: form.email_from_name,
    email_to: form.email_to,
    remind_ahead_days: mergedDays(),
    message_template: form.message_template,
  })
}

async function save() {
  saving.value = true
  message.value = ''
  try {
    await persist()
    message.value = t('settings.saved')
    messageType.value = 'ok'
  } catch (e) {
    message.value = t('settings.saveFailed')
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

async function testSend() {
  testing.value = true
  testResult.value = null
  try {
    // 先保存当前配置，确保测试使用最新填写值
    await persist()
    testResult.value = await testReminder()
  } catch (e) {
    testResult.value = { email: false, serverchan: false, note: String(e) }
  } finally {
    testing.value = false
  }
}

onMounted(load)
</script>
