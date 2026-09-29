<template>
  <div class="space-y-6">
    <!-- 概览卡片（点击可下钻到明细） -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <button
        type="button"
        @click="drillTotal"
        :title="t('stats.clickHint')"
        class="text-left bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 hover:border-primary-200 dark:hover:border-primary-800"
      >
        <div class="text-3xl mb-2">👥</div>
        <div class="text-2xl font-bold text-gray-800 dark:text-white">{{ stats.total }}</div>
        <div class="text-sm text-gray-400">{{ t('stats.total') }}</div>
      </button>
      <button
        type="button"
        @click="drillUpcoming30"
        :title="t('stats.clickHint')"
        class="text-left bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 hover:border-primary-200 dark:hover:border-primary-800"
      >
        <div class="text-3xl mb-2">🎂</div>
        <div class="text-2xl font-bold text-primary-500">{{ stats.upcoming_count }}</div>
        <div class="text-sm text-gray-400">{{ t('stats.upcoming30') }}</div>
      </button>
      <button
        type="button"
        @click="drillWeek"
        :title="t('stats.clickHint')"
        class="text-left bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 hover:border-primary-200 dark:hover:border-primary-800"
      >
        <div class="text-3xl mb-2">📅</div>
        <div class="text-2xl font-bold text-green-500">{{ upcoming7 }}</div>
        <div class="text-sm text-gray-400">{{ t('stats.thisWeek') }}</div>
      </button>
      <button
        type="button"
        @click="drillToday"
        :title="t('stats.clickHint')"
        class="text-left bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 hover:border-primary-200 dark:hover:border-primary-800"
      >
        <div class="text-3xl mb-2">🎁</div>
        <div class="text-2xl font-bold text-amber-500">{{ upcomingToday }}</div>
        <div class="text-sm text-gray-400">{{ t('home.today') }}</div>
      </button>
    </div>

    <!-- 分类统计（点击条形可下钻） -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">📂 {{ t('stats.byCategory') }}</h3>

      <div v-if="Object.keys(stats.categories).length > 0" class="space-y-3">
        <button
          v-for="(count, cat) in stats.categories"
          :key="cat"
          type="button"
          @click="drillCategory(cat)"
          :title="t('stats.clickHint')"
          class="w-full flex items-center gap-3 rounded-lg px-2 py-1 -mx-2 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50"
        >
          <span class="text-sm text-gray-600 dark:text-gray-400 w-16 text-left truncate">{{ t('form.categories.' + categoryKey(cat) ) }}</span>
          <div class="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
              :style="{
                width: (count / stats.total * 100) + '%',
                background: getCategoryColor(cat)
              }"
            >
              <span class="text-xs font-bold text-white">{{ count }}</span>
            </div>
          </div>
        </button>
      </div>

      <div v-else class="text-center py-8 text-gray-400">
        {{ t('common.noData') }}
      </div>
    </div>

    <!-- 分类饼图（点击图例可下钻） -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">📊 {{ lang === 'zh' ? '分布概览' : 'Distribution' }}</h3>

      <div v-if="Object.keys(stats.categories).length > 0" class="flex flex-col sm:flex-row items-center gap-6">
        <div class="relative w-40 h-40 flex-shrink-0">
          <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
            <circle
              v-for="(item, i) in pieData"
              :key="i"
              cx="18" cy="18" r="14"
              fill="none"
              :stroke="item.color"
              stroke-width="4"
              :stroke-dasharray="item.dashArray"
              :stroke-dashoffset="item.offset"
              class="transition-all duration-500 cursor-pointer hover:opacity-80"
              @click="drillCategory(item.catKey)"
            >
              <title>{{ item.name }} · {{ item.count }}</title>
            </circle>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800 dark:text-white">{{ stats.total }}</div>
              <div class="text-xs text-gray-400">{{ t('stats.total') }}</div>
            </div>
          </div>
        </div>

        <div class="flex-1 grid grid-cols-2 gap-1">
          <button
            v-for="(item, i) in pieData"
            :key="i"
            type="button"
            @click="drillCategory(item.catKey)"
            :title="t('stats.clickHint')"
            class="flex items-center gap-2 rounded-lg px-2 py-1.5 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50"
          >
            <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ background: item.color }" />
            <span class="text-sm text-gray-600 dark:text-gray-400 truncate">{{ item.name }}</span>
            <span class="text-sm font-bold text-gray-800 dark:text-white ml-auto">{{ item.count }}</span>
          </button>
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-400">
        {{ t('common.noData') }}
      </div>
    </div>

    <!-- 下钻明细弹窗 -->
    <StatsDrilldownModal
      :show="drill.show"
      :title="drill.title"
      :icon="drill.icon"
      :color="drill.color"
      :items="drill.items"
      @close="closeDrill"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'
import StatsDrilldownModal from '../components/StatsDrilldownModal.vue'

const { t, lang } = useI18n()
const { getStats, listUpcoming, listBirthdays } = useApi()

const stats = ref({ total: 0, categories: {}, upcoming_count: 0 })
const upcoming = ref([])
const allBirthdays = ref([])

const weekList = computed(() => upcoming.value.filter(b => b.days_until <= 7))
const todayList = computed(() => upcoming.value.filter(b => b.days_until === 0))
const upcoming7 = computed(() => weekList.value.length)
const upcomingToday = computed(() => todayList.value.length)

function categoryKey(cat) {
  return cat
}

const categoryColors = {
  '朋友': '#FF6B6B',
  '家人': '#4ECDC4',
  '同事': '#96CEB4',
  '客户': '#DDA0DD',
  '同学': '#87CEEB',
  'other': '#F0E68C',
}

const categoryEmoji = {
  '朋友': '👫',
  '家人': '🏠',
  '同事': '💼',
  '同学': '🎓',
  '客户': '🤝',
  'other': '📌',
}

function getCategoryColor(cat) {
  return categoryColors[cat] || '#9CA3AF'
}

const pieData = computed(() => {
  const total = stats.value.total
  if (total === 0) return []

  const categories = Object.entries(stats.value.categories)
  let offset = 0

  return categories.map(([name, count]) => {
    const percent = count / total
    const dashArray = `${(percent * 100).toFixed(1)} ${(100 - percent * 100).toFixed(1)}`
    const item = {
      catKey: name,
      name: t('form.categories.' + categoryKey(name)),
      count,
      color: getCategoryColor(name),
      dashArray,
      offset: -offset.toFixed(2),
    }
    offset += percent * 100
    return item
  })
})

// ==== 下钻 ====
const drill = ref({ show: false, title: '', icon: '📂', color: '#f97316', items: [] })

function openDrill(title, icon, color, items) {
  drill.value = { show: true, title, icon, color, items }
}
function closeDrill() {
  drill.value = { ...drill.value, show: false }
}

function drillTotal() {
  openDrill(t('stats.total'), '👥', '#f97316', allBirthdays.value)
}
function drillUpcoming30() {
  openDrill(t('stats.upcoming30'), '🎂', '#f97316', upcoming.value)
}
function drillWeek() {
  openDrill(t('stats.thisWeek'), '📅', '#22c55e', weekList.value)
}
function drillToday() {
  openDrill(t('home.today'), '🎁', '#f59e0b', todayList.value)
}
function drillCategory(cat) {
  const items = allBirthdays.value.filter(b => b.category === cat)
  openDrill(
    t('form.categories.' + categoryKey(cat)),
    categoryEmoji[cat] || '📂',
    getCategoryColor(cat),
    items,
  )
}

async function loadData() {
  try {
    const [s, u, all] = await Promise.all([getStats(), listUpcoming(30), listBirthdays()])
    stats.value = s
    upcoming.value = u
    allBirthdays.value = all
  } catch (e) {
    console.error('Stats load failed:', e)
  }
}

onMounted(loadData)
</script>
