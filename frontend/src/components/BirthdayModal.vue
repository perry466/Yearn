<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md z-10 max-h-[90vh] overflow-y-auto">

          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
            <div class="flex items-center gap-2">
              <span class="text-xl">🎂</span>
              <h2 class="text-lg font-bold text-gray-800 dark:text-white">
                {{ isEdit ? t('form.editTitle') : t('form.addTitle') }}
              </h2>
            </div>
            <button
              @click="$emit('close')"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="p-6 space-y-5">

            <!-- 姓名 -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ t('form.name') }} <span class="text-red-400">*</span>
              </label>
              <input
                ref="nameInputRef"
                v-model="form.name"
                type="text"
                required
                :placeholder="t('form.namePlaceholder')"
                class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm placeholder-gray-300 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <!-- 生日日期选择卡片 -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ t('form.dateType') }}
              </label>

              <!-- 公历 / 农历 切换 -->
              <div class="flex bg-gray-100 dark:bg-gray-700 rounded-xl p-1 mb-3">
                <button
                  type="button"
                  @click="switchToSolar"
                  class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all"
                  :class="!form.is_lunar
                    ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-white shadow-sm ring-1 ring-gray-200 dark:ring-gray-500'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
                >
                  ☀️ {{ t('form.solar') }}
                </button>
                <button
                  type="button"
                  @click="switchToLunar"
                  class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all"
                  :class="form.is_lunar
                    ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-white shadow-sm ring-1 ring-gray-200 dark:ring-gray-500'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
                >
                  🌙 {{ t('form.lunar') }}
                </button>
              </div>

              <!-- 公历日期 -->
              <div v-if="!form.is_lunar">
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                  📅 {{ t('form.solarDate') }}
                </label>
                <div class="relative">
                  <input
                    v-model="form.solar_date"
                    type="date"
                    :max="todayStr"
                    required
                    class="w-full px-4 py-3 rounded-xl border-2 border-primary-200 dark:border-primary-700 bg-primary-50/50 dark:bg-primary-900/20 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all cursor-pointer"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 text-primary-400 pointer-events-none">📅</span>
                </div>
                <p class="text-xs text-gray-400 mt-1.5">{{ lang === 'zh' ? '出生日期不能是未来' : "Can't be in the future" }}</p>
              </div>

              <!-- 农历日期 -->
              <div v-else>
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                  🌙 {{ t('form.lunarDay') }}
                </label>

                <!-- 农历选择面板 -->
                <div class="bg-primary-50/50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-700 rounded-xl p-4 space-y-3">
                  <div class="grid grid-cols-3 gap-2">
                    <!-- 年 -->
                    <div class="relative">
                      <select
                        v-model="lunarPick.year"
                        :max="currentYear"
                        class="w-full appearance-none px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none cursor-pointer pr-7"
                      >
                        <option v-for="y in yearOptionsUpToNow" :key="y" :value="y">{{ y }}</option>
                      </select>
                      <span class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none">
                        {{ lang === 'zh' ? '年' : '' }}
                      </span>
                    </div>
                    <!-- 月 -->
                    <div class="relative">
                      <select
                        v-model="lunarPick.month"
                        class="w-full appearance-none px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none cursor-pointer pr-7"
                      >
                        <option v-for="m in 12" :key="m" :value="m">{{ lunarMonthNames[m - 1] }}</option>
                      </select>
                      <span class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none">
                        {{ lang === 'zh' ? '月' : '' }}
                      </span>
                    </div>
                    <!-- 日 -->
                    <div class="relative">
                      <select
                        v-model="lunarPick.day"
                        class="w-full appearance-none px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none cursor-pointer pr-7"
                      >
                        <option v-for="d in lunarDaysInMonth" :key="d" :value="d">{{ lunarDayNames[d - 1] }}</option>
                      </select>
                      <span class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none">
                        {{ lang === 'zh' ? '日' : '' }}
                      </span>
                    </div>
                  </div>

                  <!-- 闰月开关 -->
                  <label class="flex items-center gap-2.5 cursor-pointer group select-none">
                    <span class="relative inline-block">
                      <input
                        type="checkbox"
                        v-model="lunarPick.is_leap"
                        class="peer sr-only"
                      />
                      <span
                        class="block w-9 h-5 rounded-full transition-colors"
                        :class="lunarPick.is_leap ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'"
                      ></span>
                      <span
                        class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                        :class="lunarPick.is_leap ? 'left-[18px]' : 'left-0.5'"
                      ></span>
                    </span>
                    <span class="text-sm text-gray-600 dark:text-gray-300 group-hover:text-primary-500 transition-colors">
                      🌸 {{ t('form.isLeapMonth') }}
                    </span>
                  </label>

                  <!-- 预览文字 -->
                  <p class="text-xs text-center text-primary-600 dark:text-primary-300 font-medium">
                    🌙 {{ lunarDisplayText }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 分类 -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ t('form.category') }}
              </label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="cat in categoryOptions"
                  :key="cat.key"
                  type="button"
                  @click="form.category = cat.key"
                  class="flex items-center justify-center gap-1.5 px-2 py-2 rounded-xl border text-xs font-medium transition-all"
                  :class="form.category === cat.key
                    ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300 ring-1 ring-primary-400'
                    : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-primary-300 dark:hover:border-primary-600 hover:bg-primary-50/50 dark:hover:bg-primary-900/20'"
                >
                  <span>{{ cat.emoji }}</span>
                  <span>{{ t('form.categories.' + cat.key) }}</span>
                </button>
              </div>
            </div>

            <!-- 备注 -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ t('form.remark') }}
                <span class="text-gray-400 font-normal ml-1">· {{ lang === 'zh' ? '可选' : 'Optional' }}</span>
              </label>
              <textarea
                v-model="form.remark"
                rows="2"
                :placeholder="t('form.remarkPlaceholder')"
                class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white text-sm placeholder-gray-300 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all resize-none"
              />
            </div>

            <!-- 提醒开关 -->
            <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-700/40 rounded-xl px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="text-base">🔔</span>
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('form.enabled') }}</span>
              </div>
              <button
                type="button"
                @click="form.is_enabled = !form.is_enabled"
                class="relative w-11 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                :class="form.is_enabled ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'"
              >
                <span
                  class="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                  :class="form.is_enabled ? 'left-6' : 'left-0.5'"
                />
              </button>
            </div>

            <!-- 提交 -->
            <div class="flex gap-3 pt-1">
              <button
                type="button"
                @click="$emit('close')"
                class="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-semibold text-sm"
              >
                {{ t('common.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="loading || !form.name.trim() || !isDateValid"
                class="flex-1 px-4 py-3 rounded-xl bg-primary-500 hover:bg-primary-600 active:bg-primary-700 text-white font-semibold text-sm transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? (lang === 'zh' ? '保存中…' : 'Saving…') : t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  show: Boolean,
  birthday: { type: Object, default: null },
})

const emit = defineEmits(['close', 'save'])
const { t, lang } = useI18n()

// 今天是字符串形式，用于 date input max 属性
const today = new Date()
const todayStr = today.toISOString().split('T')[0]
const currentYear = today.getFullYear()

const categoryOptions = [
  { key: 'family',    emoji: '👨‍👩‍👧' },
  { key: 'friend',    emoji: '🤝' },
  { key: 'colleague', emoji: '💼' },
  { key: 'classmate', emoji: '🎒' },
  { key: 'client',    emoji: '🤵' },
  { key: 'other',     emoji: '🌟' },
]

const lunarMonthNames = ['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','冬月','腊月']
const lunarDayNames = [
  '初一','初二','初三','初四','初五','初六','初七','初八','初九','初十',
  '十一','十二','十三','十四','十五','十六','十七','十八','十九','二十',
  '廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十'
]

// 年份：1940 到今年
const yearOptionsUpToNow = Array.from(
  { length: currentYear - 1940 + 1 },
  (_, i) => currentYear - i
)

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
const nameInputRef = ref(null)

const lunarPick = ref({ year: 2000, month: 1, day: 1, is_leap: false })

// 农历天数：正月和腊月30天，其他29天
const lunarDaysInMonth = computed(() => {
  return [1, 12].includes(lunarPick.value.month) ? 30 : 29
})

const lunarDisplayText = computed(() => {
  const { year, month, day, is_leap } = lunarPick.value
  const leapStr = is_leap ? (lang.value === 'zh' ? '闰' : 'Leap ') : ''
  return `${year}${lang.value === 'zh' ? '年' : ' '}${leapStr}${lunarMonthNames[month - 1]}${lunarDayNames[day - 1]}`
})

// 日期合法性：不能选未来
const isDateValid = computed(() => {
  if (form.value.is_lunar) {
    return lunarPick.value.year <= currentYear
  }
  if (!form.value.solar_date) return true
  return form.value.solar_date <= todayStr
})

// 切换到公历
function switchToSolar() {
  form.value.is_lunar = false
}

// 切换到农历
function switchToLunar() {
  form.value.is_lunar = true
}

// 打开弹窗时自动聚焦姓名
watch(() => props.show, async (val) => {
  if (val) {
    await nextTick()
    nameInputRef.value?.focus()
  }
})

// 填充表单数据
watch(() => props.show, (val) => {
  if (val) {
    if (props.birthday) {
      isEdit.value = true
      form.value = {
        name:       props.birthday.name       || '',
        solar_date: props.birthday.solar_date || '',
        lunar_date: props.birthday.lunar_date || '',
        is_lunar:   props.birthday.is_lunar   || false,
        category:   props.birthday.category   || 'friend',
        remark:     props.birthday.remark     || '',
        is_enabled: props.birthday.is_enabled !== false,
      }
      if (props.birthday.is_lunar && props.birthday.lunar_date) {
        const parts = props.birthday.lunar_date.split('-')
        lunarPick.value = {
          year:   parseInt(parts[0]) || 2000,
          month:  parseInt(parts[1]) || 1,
          day:    parseInt(parts[2]) || 1,
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

// 农历日超界修正
watch(() => lunarPick.value.month, () => {
  if (lunarPick.value.day > lunarDaysInMonth.value) {
    lunarPick.value.day = lunarDaysInMonth.value
  }
})

async function handleSubmit() {
  if (!form.value.name.trim()) return
  if (!isDateValid.value) return

  if (form.value.is_lunar) {
    const lp = lunarPick.value
    form.value.lunar_date = `${lp.year}-${String(lp.month).padStart(2,'0')}-${String(lp.day).padStart(2,'0')}${lp.is_leap ? '-leap' : ''}`
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
