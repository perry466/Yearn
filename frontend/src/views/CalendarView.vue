<template>
  <div class="space-y-6">
    <!-- 头部：年月切换 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button
          @click="prevMonth"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          ◀
        </button>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white min-w-[140px] text-center">
          {{ currentYear }} {{ lang === 'zh' ? '年' : '' }} {{ currentMonth + 1 }} {{ lang === 'zh' ? '月' : '' }}
        </h2>
        <button
          @click="nextMonth"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          ▶
        </button>
      </div>
      <button
        @click="goToday"
        class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        {{ t('home.today') }}
      </button>
    </div>

    <!-- 星期标题 -->
    <div class="grid grid-cols-7 gap-1">
      <div
        v-for="(day, i) in weekDays"
        :key="i"
        class="text-center text-sm font-medium text-gray-400 py-2"
      >
        {{ day }}
      </div>
    </div>

    <!-- 日历格子 -->
    <div class="grid grid-cols-7 gap-1">
      <div
        v-for="i in firstDayOfMonth"
        :key="'empty-' + i"
        class="min-h-[80px] sm:min-h-[100px] rounded-xl"
      />

      <div
        v-for="day in daysInMonth"
        :key="day"
        class="min-h-[80px] sm:min-h-[100px] rounded-xl p-2 border transition-all"
        :class="isToday(day)
          ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-700'
          : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-700'"
        @click="selectDate(day)"
      >
        <div
          class="w-7 h-7 flex items-center justify-center rounded-full text-sm font-medium mb-1"
          :class="isToday(day)
            ? 'bg-primary-500 text-white'
            : 'text-gray-600 dark:text-gray-400'"
        >
          {{ day }}
        </div>

        <div class="space-y-0.5">
          <div
            v-for="b in getBirthdaysOnDay(day)"
            :key="b.id"
            class="text-xs px-1.5 py-0.5 rounded truncate cursor-pointer hover:bg-primary-50 dark:hover:bg-primary-900/30"
            :class="isToday(day)
              ? 'text-primary-700 dark:text-primary-300'
              : 'text-gray-600 dark:text-gray-400'"
            :title="b.name + ' - ' + (b.is_lunar ? (lang === 'zh' ? '农历' : 'Lunar') : (lang === 'zh' ? '公历' : 'Solar')) + ' ' + (b.is_lunar ? b.lunar_date : b.solar_date)"
            @click.stop="$emit('edit', b)"
          >
            🎂 {{ b.name }}
          </div>
        </div>
      </div>
    </div>

    <!-- 当月生日列表 -->
    <div v-if="monthBirthdays.length > 0" class="bg-white dark:bg-gray-800 rounded-2xl p-4 border border-gray-100 dark:border-gray-700">
      <h3 class="font-bold text-gray-800 dark:text-white mb-3">
        📅 {{ currentYear }} {{ lang === 'zh' ? '年' : '' }} {{ currentMonth + 1 }} {{ lang === 'zh' ? '月' : '' }} — {{ monthBirthdays.length }} {{ lang === 'zh' ? '人' : 'people' }}
      </h3>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="b in monthBirthdays"
          :key="b.id"
          class="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 rounded-lg px-3 py-1.5 cursor-pointer hover:bg-primary-50 dark:hover:bg-primary-900/30 transition-colors"
          @click="$emit('edit', b)"
        >
          <span class="text-lg">{{ getEmoji(b.days_until) }}</span>
          <div>
            <div class="text-sm font-medium text-gray-800 dark:text-white">{{ b.name }}</div>
            <div class="text-xs text-gray-400">{{ b.upcoming_date }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'

const { t, lang } = useI18n()
const { getCalendar } = useApi()

const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())
const monthBirthdays = ref([])

const weekDays = computed(() => {
  if (lang.value === 'zh') return [t('calendar.sun'), t('calendar.mon'), t('calendar.tue'), t('calendar.wed'), t('calendar.thu'), t('calendar.fri'), t('calendar.sat')]
  return [t('calendar.sun'), t('calendar.mon'), t('calendar.tue'), t('calendar.wed'), t('calendar.thu'), t('calendar.fri'), t('calendar.sat')]
})

const emit = defineEmits(['edit'])

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})

const firstDayOfMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).getDay()
})

function isToday(day) {
  return (
    today.getFullYear() === currentYear.value &&
    today.getMonth() === currentMonth.value &&
    today.getDate() === day
  )
}

function getBirthdaysOnDay(day) {
  return monthBirthdays.value.filter(b => {
    const d = new Date(b.upcoming_date)
    return d.getDate() === day
  })
}

function getEmoji(days) {
  if (days === 0) return '🎂'
  if (days === 1) return '⚠️'
  if (days <= 7) return '🎉'
  return '🎁'
}

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
  loadCalendar()
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  loadCalendar()
}

function goToday() {
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth()
  loadCalendar()
}

async function loadCalendar() {
  try {
    monthBirthdays.value = await getCalendar(currentYear.value, currentMonth.value + 1)
  } catch (e) {
    console.error('Calendar load failed:', e)
  }
}

function selectDate(day) {
  // could open day detail in future
}

onMounted(loadCalendar)
</script>
