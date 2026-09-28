<template>
  <div class="space-y-6">
    <!-- 概览卡片 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
        <div class="text-3xl mb-2">👥</div>
        <div class="text-2xl font-bold text-gray-800 dark:text-white">{{ stats.total }}</div>
        <div class="text-sm text-gray-400">{{ t('stats.total') }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
        <div class="text-3xl mb-2">🎂</div>
        <div class="text-2xl font-bold text-primary-500">{{ stats.upcoming_count }}</div>
        <div class="text-sm text-gray-400">{{ t('stats.upcoming30') }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
        <div class="text-3xl mb-2">📅</div>
        <div class="text-2xl font-bold text-green-500">{{ upcoming7 }}</div>
        <div class="text-sm text-gray-400">{{ lang === 'zh' ? '本周' : 'This week' }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
        <div class="text-3xl mb-2">🎁</div>
        <div class="text-2xl font-bold text-amber-500">{{ upcomingToday }}</div>
        <div class="text-sm text-gray-400">{{ t('home.today') }}</div>
      </div>
    </div>

    <!-- 分类统计 -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">📂 {{ t('stats.byCategory') }}</h3>

      <div v-if="Object.keys(stats.categories).length > 0" class="space-y-3">
        <div
          v-for="(count, cat) in stats.categories"
          :key="cat"
          class="flex items-center gap-3"
        >
          <span class="text-sm text-gray-600 dark:text-gray-400 w-16">{{ t('form.categories.' + categoryKey(cat) ) }}</span>
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
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-400">
        {{ t('common.noData') }}
      </div>
    </div>

    <!-- 分类饼图 -->
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
              class="transition-all duration-500"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800 dark:text-white">{{ stats.total }}</div>
              <div class="text-xs text-gray-400">{{ t('stats.total') }}</div>
            </div>
          </div>
        </div>

        <div class="flex-1 grid grid-cols-2 gap-2">
          <div
            v-for="(item, i) in pieData"
            :key="i"
            class="flex items-center gap-2"
          >
            <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ background: item.color }" />
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ item.name }}</span>
            <span class="text-sm font-bold text-gray-800 dark:text-white ml-auto">{{ item.count }}</span>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-400">
        {{ t('common.noData') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'

const { t, lang } = useI18n()
const { getStats, listUpcoming } = useApi()

const stats = ref({ total: 0, categories: {}, upcoming_count: 0 })
const upcoming = ref([])

const upcoming7 = computed(() => upcoming.value.filter(b => b.days_until <= 7).length)
const upcomingToday = computed(() => upcoming.value.filter(b => b.days_until === 0).length)

const categoryMap = { '朋友': 'friend', '家人': 'family', '同事': 'colleague', '客户': 'client', '同学': 'classmate', '其他': 'other' }
function categoryKey(cat) {
  return categoryMap[cat] || cat
}

const categoryColors = {
  '朋友': '#FF6B6B',
  '家人': '#4ECDC4',
  '同事': '#96CEB4',
  '客户': '#DDA0DD',
  '同学': '#87CEEB',
  '其他': '#F0E68C',
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

async function loadData() {
  try {
    const [s, u] = await Promise.all([getStats(), listUpcoming(30)])
    stats.value = s
    upcoming.value = u
  } catch (e) {
    console.error('Stats load failed:', e)
  }
}

onMounted(loadData)
</script>
