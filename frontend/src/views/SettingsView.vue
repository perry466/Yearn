<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <div class="bg-head inline-block">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white">{{ t('settings.title') }}</h2>
      <p class="text-sm text-gray-400 mt-1">{{ t('settings.subtitle') }}</p>
    </div>

    <!-- 外观 -->
    <section class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">🎨 {{ t('appearance.title') }}</h3>
      <p class="text-sm text-gray-400 mb-4">{{ t('appearance.desc') }}</p>

      <!-- 颜色模式 -->
      <div class="mb-5">
        <label class="text-sm text-gray-500">{{ t('appearance.mode') }}</label>
        <div class="mt-2 inline-flex rounded-xl border border-gray-200 dark:border-gray-600 p-1 bg-gray-50 dark:bg-gray-700/50">
          <button
            v-for="m in modeOptions"
            :key="m.value"
            type="button"
            @click="state.mode = m.value"
            class="px-4 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="state.mode === m.value
              ? 'bg-primary-500 text-white'
              : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700'"
          >
            {{ m.label }}
          </button>
        </div>
      </div>

      <!-- 界面不透明度 -->
      <div class="mb-5">
        <label class="text-sm text-gray-500">{{ t('appearance.uiOpacity') }}</label>
        <div class="mt-2 flex items-center gap-3">
          <input
            type="range"
            min="40"
            max="100"
            step="5"
            :value="Math.round(state.uiAlpha * 100)"
            @input="state.uiAlpha = +$event.target.value / 100"
            class="w-48 accent-primary-500"
          />
          <span class="text-sm text-gray-600 dark:text-gray-300 tabular-nums">
            {{ Math.round(state.uiAlpha * 100) }}%
          </span>
        </div>
        <p class="text-xs text-gray-400 mt-1">{{ t('appearance.uiOpacityHint') }}</p>
      </div>

      <!-- 主题色 -->
      <div class="mb-5">
        <label class="text-sm text-gray-500">{{ t('appearance.accent') }}</label>
        <div class="mt-2 flex flex-wrap gap-2.5">
          <button
            v-for="a in accentPresets"
            :key="a.id"
            type="button"
            @click="setAccent(a.id)"
            class="flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-full border transition-colors"
            :class="state.accent === a.id
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
            :title="a.name[lang]"
          >
            <span
              class="w-6 h-6 rounded-full ring-2 ring-white dark:ring-gray-800 shadow"
              :style="{ backgroundColor: a.color }"
            ></span>
            <span
              class="text-sm"
              :class="state.accent === a.id ? 'text-primary-600 dark:text-primary-400 font-medium' : 'text-gray-600 dark:text-gray-300'"
            >{{ a.name[lang] }}</span>
          </button>
        </div>
      </div>

      <!-- 背景 -->
      <div>
        <label class="text-sm text-gray-500">{{ t('appearance.bg') }}</label>
        <div class="mt-2 flex items-center gap-2 flex-wrap">
          <div class="inline-flex rounded-xl border border-gray-200 dark:border-gray-600 p-1 bg-gray-50 dark:bg-gray-700/50">
            <button
              v-for="bt in bgTypeOptions"
              :key="bt.value"
              type="button"
              @click="setBgType(bt.value)"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="currentBg.type === bt.value
                ? 'bg-primary-500 text-white'
                : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700'"
            >
              {{ bt.label }}
            </button>
          </div>

          <!-- 编辑哪个模式的背景 -->
          <div class="inline-flex rounded-xl border border-gray-200 dark:border-gray-600 p-1 bg-gray-50 dark:bg-gray-700/50 sm:ml-auto">
            <button
              v-for="em in editModeOptions"
              :key="em.value"
              type="button"
              @click="editingMode = em.value"
              class="px-3 py-1.5 rounded-lg text-sm transition-colors"
              :class="editingMode === em.value
                ? 'bg-primary-500 text-white font-medium'
                : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700'"
            >
              {{ em.label }}
            </button>
          </div>
        </div>

        <!-- 纯色 -->
        <div v-if="currentBg.type === 'color'" class="mt-4 flex items-center gap-3">
          <input type="color" v-model="currentBg.color" class="w-10 h-10 rounded-lg border border-gray-200 dark:border-gray-600 bg-transparent cursor-pointer" />
          <input type="text" v-model="currentBg.color" class="w-32 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm font-mono" />
        </div>

        <!-- 渐变 -->
        <div v-else-if="currentBg.type === 'gradient'" class="mt-4 space-y-4">
          <div>
            <div class="text-xs text-gray-400 mb-2">{{ t('appearance.bgPreset') }}</div>
            <div class="flex flex-wrap gap-2.5">
              <button
                v-for="g in gradientPresets"
                :key="g.id"
                type="button"
                @click="applyGradient(g)"
                class="w-16 h-11 rounded-lg border-2 transition-all"
                :class="currentBg.from === g.from && currentBg.to === g.to && currentBg.angle === g.angle
                  ? 'border-primary-500 scale-105'
                  : 'border-transparent hover:scale-105'"
                :style="{ backgroundImage: gradientCss(g) }"
                :title="g.name[lang]"
              ></button>
            </div>
          </div>
          <div class="flex items-center gap-3 flex-wrap">
            <label class="text-sm text-gray-500">{{ t('appearance.bgFrom') }}</label>
            <input type="color" v-model="currentBg.from" class="w-9 h-9 rounded-lg border border-gray-200 dark:border-gray-600 bg-transparent cursor-pointer" />
            <label class="text-sm text-gray-500 ml-2">{{ t('appearance.bgTo') }}</label>
            <input type="color" v-model="currentBg.to" class="w-9 h-9 rounded-lg border border-gray-200 dark:border-gray-600 bg-transparent cursor-pointer" />
            <label class="text-sm text-gray-500 ml-2">{{ t('appearance.bgAngle') }}</label>
            <input type="range" min="0" max="360" v-model.number="currentBg.angle" class="flex-1 min-w-[120px] accent-primary-500" />
            <span class="text-xs text-gray-400 w-10 text-right">{{ currentBg.angle }}°</span>
          </div>
        </div>

        <!-- 图片 -->
        <div v-else-if="currentBg.type === 'image'" class="mt-4 space-y-3">
          <div class="flex items-center gap-2 flex-wrap">
            <input
              type="text"
              :value="currentBg.url"
              @input="onUrlInput"
              :placeholder="t('appearance.bgUrlPlaceholder')"
              class="flex-1 min-w-[200px] px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm"
            />
            <label class="px-4 py-2 rounded-lg border border-primary-500 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 text-sm font-medium cursor-pointer transition-colors whitespace-nowrap">
              {{ t('appearance.upload') }}
              <input type="file" accept="image/*" class="hidden" @change="onUpload" />
            </label>
          </div>
          <div v-if="currentBg.stored" class="text-xs text-emerald-600 dark:text-emerald-400">
            {{ t('appearance.uploadedHint') }}
          </div>
          <div v-if="uploadError" class="text-xs text-red-500">{{ uploadError }}</div>
          <div class="flex items-center gap-2">
            <label class="text-sm text-gray-500 w-14">{{ t('appearance.bgFit') }}</label>
            <div class="inline-flex rounded-lg border border-gray-200 dark:border-gray-600 p-1 bg-gray-50 dark:bg-gray-700/50">
              <button
                v-for="ft in fitOptions"
                :key="ft.value"
                type="button"
                @click="currentBg.fit = ft.value"
                class="px-3 py-1 rounded-md text-sm transition-colors"
                :class="currentBg.fit === ft.value
                  ? 'bg-primary-500 text-white font-medium'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700'"
              >
                {{ ft.label }}
              </button>
            </div>
          </div>
          <div v-if="bgInfo" class="text-xs" :class="bgWarn ? 'text-amber-600 dark:text-amber-400' : 'text-gray-400'">
            {{ bgInfo }}
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-500 w-14">{{ t('appearance.bgBlur') }}</label>
              <input type="range" min="0" max="30" v-model.number="currentBg.blur" class="flex-1 accent-primary-500" />
              <span class="text-xs text-gray-400 w-10 text-right">{{ currentBg.blur }}px</span>
            </div>
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-500 w-14">{{ t('appearance.bgDim') }}</label>
              <input type="range" min="0" max="90" :value="Math.round(currentBg.dim * 100)" @input="currentBg.dim = $event.target.value / 100" class="flex-1 accent-primary-500" />
              <span class="text-xs text-gray-400 w-10 text-right">{{ Math.round(currentBg.dim * 100) }}%</span>
            </div>
          </div>
        </div>

        <p class="text-xs text-gray-400 mt-3">{{ t('appearance.bgTip') }}</p>
      </div>
    </section>

    <!-- 提醒频率 -->
    <section class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
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
    <section class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
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
    <section class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
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
    <section class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
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
      class="ui-panel rounded-2xl p-6 border border-gray-100 dark:border-gray-700"
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import { ACCENT_PRESETS, GRADIENT_PRESETS, gradientCss } from '../theme/presets'

const { t, tf, lang } = useI18n()
const { getSettings, updateSettings, testReminder } = useApi()
const { state, setAccent, saveNow, resolveBgUrl, setImageFile, setImageUrl } = useTheme()

const accentPresets = ACCENT_PRESETS
const gradientPresets = GRADIENT_PRESETS

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

// —— 外观设置（写入 localStorage，改即生效、无需点保存）——
const editingMode = ref('light')
const uploadError = ref('')
const currentBg = computed(() => state.background[editingMode.value])

// 背景图清晰度诊断：算出「铺满/完整」实际需要把图放大多少倍
const bgInfo = ref('')
const bgWarn = ref(false)

function probeImageSize(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve({ w: img.naturalWidth, h: img.naturalHeight })
    img.onerror = () => reject(new Error('load failed'))
    img.src = src
  })
}

watch(
  () => [
    editingMode.value,
    currentBg.value.type,
    currentBg.value.url,
    currentBg.value.stored,
    currentBg.value.ph,
    currentBg.value.fit,
    currentBg.value.w,
    currentBg.value.h,
  ],
  async () => {
    bgInfo.value = ''
    bgWarn.value = false
    const bg = currentBg.value
    if (!bg || bg.type !== 'image') return
    const src = resolveBgUrl(editingMode.value)
    if (!src) return
    let w = bg.w || 0
    let h = bg.h || 0
    if (!w || !h) {
      try {
        const d = await probeImageSize(src)
        w = d.w
        h = d.h
      } catch (e) {
        return
      }
    }
    const sw = Math.round((window.innerWidth || 0) * (window.devicePixelRatio || 1))
    const sh = Math.round((window.innerHeight || 0) * (window.devicePixelRatio || 1))
    // 铺满=取大值（可能放大），完整=取小值
    const scale = (bg.fit === 'contain' ? Math.min : Math.max)(sw / w, sh / h)
    bgWarn.value = scale > 1.02
    bgInfo.value = tf(bgWarn.value ? 'appearance.bgInfoWarn' : 'appearance.bgInfo', {
      w,
      h,
      sw,
      sh,
      k: scale.toFixed(2),
    })
  },
  { immediate: true },
)

const modeOptions = computed(() => [
  { value: 'light', label: t('appearance.modeLight') },
  { value: 'dark', label: t('appearance.modeDark') },
  { value: 'system', label: t('appearance.modeSystem') },
])
const bgTypeOptions = computed(() => [
  { value: 'none', label: t('appearance.bgNone') },
  { value: 'color', label: t('appearance.bgColor') },
  { value: 'gradient', label: t('appearance.bgGradient') },
  { value: 'image', label: t('appearance.bgImage') },
])
const editModeOptions = computed(() => [
  { value: 'light', label: t('appearance.modeLight') },
  { value: 'dark', label: t('appearance.modeDark') },
])
const fitOptions = computed(() => [
  { value: 'cover', label: t('appearance.bgFitCover') },
  { value: 'contain', label: t('appearance.bgFitContain') },
])

function setBgType(type) {
  currentBg.value.type = type
}

function applyGradient(g) {
  const bg = currentBg.value
  bg.type = 'gradient'
  bg.from = g.from
  bg.to = g.to
  bg.angle = g.angle
}

// 上传：原图直存 IndexedDB（不做二次压缩），清晰度不受损
async function onUpload(e) {
  uploadError.value = ''
  const file = e.target.files && e.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    uploadError.value = t('appearance.uploadFailed')
    return
  }
  try {
    const ok = await setImageFile(editingMode.value, file)
    if (!ok) uploadError.value = t('appearance.uploadFailed')
  } catch (err) {
    console.warn('[theme] 上传背景图失败：', err)
    uploadError.value = t('appearance.uploadFailed')
  }
  e.target.value = ''
}

function onUrlInput(e) {
  const val = e.target.value.trim()
  setImageUrl(editingMode.value, val)
}

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
