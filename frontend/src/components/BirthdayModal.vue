<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md z-10 max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white dark:bg-gray-800 flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700 z-10">
            <h2 class="text-lg font-bold text-gray-800 dark:text-white">
              {{ isEdit ? '✏️ ' + t('form.editTitle') : '➕ ' + t('form.addTitle') }}
            </h2>
            <button
              @click="$emit('close')"
              class="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
            <!-- 姓名 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.name') }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                :placeholder="t('form.namePlaceholder')"
                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <!-- 生日类型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.dateType') }}
              </label>
              <div class="flex gap-3">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="form.is_lunar" :value="false" class="text-primary-500" />
                  <span class="text-sm text-gray-600 dark:text-gray-300">{{ t('form.solar') }}</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="form.is_lunar" :value="true" class="text-primary-500" />
                  <span class="text-sm text-gray-600 dark:text-gray-300">{{ t('form.lunar') }}</span>
                </label>
              </div>
            </div>

            <!-- 公历日期 -->
            <div v-if="!form.is_lunar">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.solarDate') }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.solar_date"
                type="date"
                required
                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <!-- 农历日期 -->
            <div v-else class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.lunarDay') }} <span class="text-red-500">*</span>
              </label>

              <div class="grid grid-cols-3 gap-2">
                <select
                  v-model="lunarPick.year"
                  class="px-2 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                >
                  <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}{{ lang === 'zh' ? '年' : '' }}</option>
                </select>

                <select
                  v-model="lunarPick.month"
                  class="px-2 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                >
                  <option v-for="m in 12" :key="m" :value="m">{{ lunarMonthNames[m - 1] }}</option>
                </select>

                <select
                  v-model="lunarPick.day"
                  class="px-2 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                >
                  <option v-for="d in 30" :key="d" :value="d">{{ lunarDayNames[d - 1] }}</option>
                </select>
              </div>

              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="lunarPick.is_leap" class="text-primary-500 rounded" />
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('form.isLeapMonth') }}</span>
              </label>

              <p class="text-xs text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 rounded-lg px-3 py-2">
                📅 {{ lang === 'zh' ? '农历' : 'Lunar' }} {{ lunarDisplayText }}
                <span v-if="solarPreview" class="text-gray-500 dark:text-gray-400">
                  · {{ lang === 'zh' ? '对应公历' : '≈ Solar' }} {{ solarPreview }}
                </span>
              </p>
            </div>

            <!-- 分类 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.category') }}
              </label>
              <select
                v-model="form.category"
                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              >
                <option v-for="cat in categoryKeys" :key="cat" :value="cat">{{ t('form.categories.' + cat) }}</option>
              </select>
            </div>

            <!-- 备注 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('form.remark') }}
              </label>
              <textarea
                v-model="form.remark"
                rows="2"
                :placeholder="t('form.remarkPlaceholder')"
                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all resize-none"
              />
            </div>

            <!-- 提醒开关 -->
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('form.enabled') }}</span>
              <button
                type="button"
                @click="form.is_enabled = !form.is_enabled"
                class="relative w-12 h-6 rounded-full transition-colors"
                :class="form.is_enabled ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'"
              >
                <span
                  class="absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform"
                  :class="form.is_enabled ? 'left-7' : 'left-1'"
                />
              </button>
            </div>

            <!-- 提交 -->
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="$emit('close')"
                class="flex-1 px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
              >
                {{ t('common.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="flex-1 px-4 py-2.5 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? (lang === 'zh' ? '保存中...' : 'Saving...') : t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  show: Boolean,
  birthday: { type: Object, default: null },
})

const emit = defineEmits(['close', 'save'])
const { t, lang } = useI18n()

const categoryKeys = ['friend', 'family', 'colleague', 'client', 'classmate', 'other']

const lunarMonthNames = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
const lunarDayNames = [
  '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十'
]

const yearOptions = Array.from({ length: 2030 - 1940 + 1 }, (_, i) => 1940 + i)

const defaultForm = {
  name: '',
  solar_date: '',
  lunar_date: '',
  is_lunar: false,
  category: 'friend',
  remark: '',
  is_enabled: true,
}

const form = ref({ ...defaultForm })
const loading = ref(false)
const isEdit = ref(false)

const lunarPick = ref({
  year: 2000,
  month: 1,
  day: 1,
  is_leap: false,
})

const lunarDisplayText = computed(() => {
  const m = lunarPick.value.month
  const d = lunarPick.value.day
  const monthStr = (lunarPick.value.is_leap ? (lang.value === 'zh' ? '闰' : 'Leap ') : '') + lunarMonthNames[m - 1]
  const dayStr = lunarDayNames[d - 1]
  return `${lunarPick.value.year}${lang.value === 'zh' ? '年' : ''} ${monthStr}${dayStr}`
})

const solarPreview = computed(() => {
  return lang.value === 'zh' ? '保存后自动计算' : 'Auto-calculated on save'
})

watch(() => props.show, (val) => {
  if (val) {
    if (props.birthday) {
      isEdit.value = true
      form.value = {
        name: props.birthday.name || '',
        solar_date: props.birthday.solar_date || '',
        lunar_date: props.birthday.lunar_date || '',
        is_lunar: props.birthday.is_lunar || false,
        category: props.birthday.category || 'friend',
        remark: props.birthday.remark || '',
        is_enabled: props.birthday.is_enabled !== false,
      }
      if (props.birthday.is_lunar && props.birthday.lunar_date) {
        const parts = props.birthday.lunar_date.split('-')
        lunarPick.value = {
          year: parseInt(parts[0]) || 2000,
          month: parseInt(parts[1]) || 1,
          day: parseInt(parts[2]) || 1,
          is_leap: parts[3] === '1' || parts[3] === 'leap',
        }
      }
    } else {
      isEdit.value = false
      form.value = { ...defaultForm }
      lunarPick.value = { year: 2000, month: 1, day: 1, is_leap: false }
    }
  }
})

async function handleSubmit() {
  if (!form.value.name.trim()) return

  if (form.value.is_lunar) {
    const lp = lunarPick.value
    form.value.lunar_date = `${lp.year}-${String(lp.month).padStart(2, '0')}-${String(lp.day).padStart(2, '0')}${lp.is_leap ? '-leap' : ''}`
    if (!form.value.solar_date) {
      form.value.solar_date = form.value.lunar_date
    }
  }

  loading.value = true
  try {
    await emit('save', { ...form.value, id: props.birthday?.id })
  } finally {
    loading.value = false
  }
}
</script>
