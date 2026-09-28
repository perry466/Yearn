<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <!-- 左侧固定侧边栏 -->
    <aside class="w-full lg:w-72 flex-shrink-0">
      <div class="sticky top-20 space-y-4">
        <!-- 即将到来统计卡片 -->
        <div class="bg-gradient-to-br from-primary-50 to-orange-50 dark:from-primary-900/30 dark:to-orange-900/20 rounded-2xl p-5 border border-primary-100 dark:border-primary-800/30">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-3xl">🎂</span>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('home.upcoming') }}</p>
              <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ upcomingCount }}</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('stats.upcoming30') }}</p>
        </div>

        <!-- 搜索 -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 border border-gray-100 dark:border-gray-700">
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ t('common.search') }}</label>
          <div class="relative">
            <input
              v-model="keyword"
              type="text"
              :placeholder="t('form.namePlaceholder')"
              class="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
            />
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          </div>
        </div>

        <!-- 视图切换 -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 border border-gray-100 dark:border-gray-700">
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ t('common.search') === 'Search' ? 'View' : '视图' }}</label>
          <div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              @click="viewMode = 'list'"
              class="flex-1 px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
              :class="viewMode === 'list'
                ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-white shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
            >
              📋 {{ t('home.listView') }}
            </button>
            <button
              @click="viewMode = 'card'"
              class="flex-1 px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
              :class="viewMode === 'card'
                ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-white shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
            >
              🃏 {{ t('home.cardView') }}
            </button>
          </div>
        </div>

        <!-- 操作按钮组 -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 border border-gray-100 dark:border-gray-700 space-y-2">
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ lang === 'zh' ? '操作' : 'Actions' }}</label>

          <!-- 选择按钮 -->
          <button
            v-if="selectedIds.size === 0"
            @click="enterSelectMode"
            class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 hover:text-primary-500 transition-all text-sm"
            :title="lang === 'zh' ? '勾选多条记录后批量删除' : 'Select multiple records to batch delete'"
          >
            <span>☑️</span>
            <span>{{ t('home.selectMode') }}</span>
          </button>

          <!-- 删除按钮（选中后） -->
          <div class="relative group" v-if="selectedIds.size > 0 && !confirmShow">
            <button
              @click="openBatchDelete"
              class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg border border-red-400 bg-red-50 dark:bg-red-900/30 text-red-500 hover:bg-red-100 transition-all text-sm"
            >
              <span>🗑️</span>
              <span>{{ t('home.deleteSelected') }} {{ selectedIds.size }} {{ t('common.items') }}</span>
            </button>
          </div>

          <!-- 添加按钮 -->
          <button
            @click="openAddModal"
            class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium transition-colors"
          >
            <span>➕</span>
            <span>{{ t('common.add') }}</span>
          </button>

          <!-- 取消选择 -->
          <button
            v-if="selectMode"
            @click="exitSelectMode"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 text-xs hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {{ lang === 'zh' ? '退出选择模式' : 'Exit select mode' }}
          </button>
        </div>

        </div>
    </aside>

    <!-- 右侧主内容 -->
    <div class="flex-1 min-w-0 space-y-6 pb-20">
      <!-- 即将到来列表（横向滚动） -->
      <div v-if="upcoming.length > 0" class="bg-gradient-to-r from-primary-50 to-orange-50 dark:from-primary-900/20 dark:to-orange-900/20 rounded-2xl p-4">
        <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-3">🎉 {{ t('home.upcoming') }}</h3>
        <div class="flex gap-3 overflow-x-auto pb-1">
          <div
            v-for="b in upcoming.slice(0, 10)"
            :key="b.id"
            class="flex-shrink-0 bg-white dark:bg-gray-800 rounded-xl px-4 py-3 shadow-sm border border-primary-100 dark:border-primary-800/30 min-w-[140px]"
          >
            <div class="text-xs text-primary-500 font-bold mb-1">
              {{ b.days_until === 0 ? t('home.today') : tf('home.daysUntil', { days: b.days_until }) }}
            </div>
            <div class="font-bold text-gray-800 dark:text-white truncate">{{ b.name }}</div>
            <div class="text-xs text-gray-400 mt-0.5">{{ b.upcoming_date }}</div>
          </div>
        </div>
      </div>

      <!-- 选择提示条 -->
      <transition name="slide-up">
        <div
          v-if="selectMode && selectedIds.size === 0"
          class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-2xl px-5 py-3 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <span class="text-blue-500">☑️</span>
            <span class="text-sm font-medium text-blue-700 dark:text-blue-300">
              {{ lang === 'zh' ? '已进入选择模式，点击卡片或行进行选择' : 'Select mode on — click cards/rows to select' }}
            </span>
          </div>
        </div>
      </transition>

      <!-- 已选提示 -->
      <transition name="slide-up">
        <div
          v-if="selectedIds.size > 0"
          class="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-2xl px-5 py-3 flex items-center justify-between"
        >
          <span class="text-sm font-medium text-primary-700 dark:text-primary-300">
            ✓ {{ t('home.selected') }} <strong>{{ selectedIds.size }}</strong> / {{ filteredBirthdays.length }} {{ t('common.items') }}
          </span>
          <button
            @click="selectedIds.clear(); selectedIds = new Set()"
            class="text-xs text-primary-500 hover:text-primary-700"
          >
            {{ lang === 'zh' ? '清空选择' : 'Clear' }}
          </button>
        </div>
      </transition>

      <!-- 数据列表/卡片 -->
      <transition name="fade" mode="out-in">
        <BirthdayTable
          v-if="viewMode === 'list'"
          :birthdays="pagedBirthdays"
          :selectMode="selectMode"
          :selectedIds="selectedIds"
          @toggle-select="toggleSelect"
          @toggle-all="toggleSelectAll"
          @edit="openEditModal"
          @delete="handleDelete"
        />
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          <BirthdayCard
            v-for="b in pagedBirthdays"
            :key="b.id"
            :birthday="b"
            :selectMode="selectMode"
            :selected="selectedIds.has(b.id)"
            @toggle-select="toggleSelect(b.id)"
            @edit="openEditModal"
            @delete="handleDelete"
          />
          <div
            v-if="pagedBirthdays.length === 0"
            class="col-span-full text-center py-16"
          >
            <p class="text-5xl mb-4">🎂</p>
            <p class="text-gray-400 dark:text-gray-500">
              {{ keyword ? (lang === 'zh' ? '没有找到匹配的记录' : 'No matching records') : (lang === 'zh' ? '还没有记录，添加一个吧' : 'No records yet — add one!') }}
            </p>
          </div>
        </div>
      </transition>

      <!-- 弹窗 -->
      <BirthdayModal
        :show="modalShow"
        :birthday="selectedBirthday"
        @close="modalShow = false"
        @save="handleSave"
      />

      <!-- 删除确认 -->
      <ConfirmModal
        :show="confirmShow"
        :names="confirmNames"
        @confirm="confirmDelete"
        @cancel="confirmShow = false"
      />
    </div>

    <!-- 冻结在底部的分页控制条 -->
    <transition name="slide-up">
      <div
        v-if="filteredBirthdays.length > 0"
        class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-t border-gray-200 dark:border-gray-700 shadow-lg"
      >
        <div class="max-w-7xl mx-auto px-4 py-3 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
          <!-- 左：每页大小 -->
          <div class="flex items-center gap-2 justify-start">
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('home.perPage') }}</span>
            <div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5">
              <button
                v-for="size in pageSizes"
                :key="size"
                @click="pageSize = size"
                class="px-3 py-1 rounded-md text-xs font-medium transition-colors"
                :class="pageSize === size
                  ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
              >
                {{ size }}
              </button>
            </div>
          </div>

          <!-- 中：信息 -->
          <p class="text-xs text-gray-500 dark:text-gray-400 text-center whitespace-nowrap">
            {{ t('common.total') }} <strong class="text-gray-800 dark:text-white">{{ filteredBirthdays.length }}</strong> {{ t('common.records') }}
            <span class="mx-1">·</span>
            {{ t('common.page') }} <strong class="text-gray-800 dark:text-white">{{ currentPage }}</strong> {{ t('common.of') }} {{ totalPages }}
          </p>

          <!-- 右：分页控件 -->
          <div class="flex items-center gap-1 justify-end min-w-[260px]">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="w-8 h-8 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-xs disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center"
              :title="t('common.prev')"
            >
              ←
            </button>

            <div class="hidden sm:flex items-center gap-1">
              <button
                v-for="p in visiblePages"
                :key="p"
                @click="goToPage(p)"
                class="min-w-[32px] h-8 rounded-lg text-xs font-medium transition-colors"
                :class="p === currentPage
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                {{ p }}
              </button>
            </div>

            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="w-8 h-8 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-xs disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center"
              :title="t('common.next')"
            >
              →
            </button>

            <div class="hidden md:flex items-center gap-1 ml-2 pl-2 border-l border-gray-200 dark:border-gray-700">
              <input
                v-model.number="jumpTo"
                @keyup.enter="performJump"
                type="number"
                :min="1"
                :max="totalPages"
                step="1"
                placeholder="#"
                class="w-12 h-8 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-xs text-center text-gray-800 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
              <button
                @click="performJump"
                class="h-8 px-3 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-xs font-medium transition-colors"
              >
                {{ t('common.jump') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import BirthdayTable from '../components/BirthdayTable.vue'
import BirthdayCard from '../components/BirthdayCard.vue'
import BirthdayModal from '../components/BirthdayModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useApi } from '../composables/useApi'
import { useI18n } from '../composables/useI18n'

const { t, tf, lang } = useI18n()
const { listBirthdays, listUpcoming, createBirthday, updateBirthday, deleteBirthday } = useApi()

const birthdays = ref([])
const upcoming = ref([])
const keyword = ref('')

const viewMode = ref(localStorage.getItem('viewMode') || 'list')
const modalShow = ref(false)
const selectedBirthday = ref(null)

const selectMode = ref(false)
const selectedIds = ref(new Set())
const confirmShow = ref(false)
const confirmNames = ref([])
const confirmIds = ref([])

const pageSize = ref(Number(localStorage.getItem('pageSize')) || 10)
const currentPage = ref(1)
const jumpTo = ref('')

const pageSizes = computed(() =>
  viewMode.value === 'card' ? [9, 12, 15] : [10, 15, 20]
)

const upcomingCount = computed(() => upcoming.value.length)

const filteredBirthdays = computed(() => {
  if (!keyword.value) return birthdays.value
  const kw = keyword.value.toLowerCase()
  return birthdays.value.filter(b =>
    b.name.toLowerCase().includes(kw) ||
    b.remark?.toLowerCase().includes(kw)
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBirthdays.value.length / pageSize.value))
)

const pagedBirthdays = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredBirthdays.value.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 5) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  let start = Math.max(1, cur - 2)
  let end = Math.min(total, start + 4)
  start = Math.max(1, end - 4)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

function goToPage(p) {
  if (typeof p !== 'number') return
  if (p < 1) p = 1
  if (p > totalPages.value) p = totalPages.value
  currentPage.value = p
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value--
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++
}

function performJump() {
  if (!jumpTo.value) return
  const n = Number(jumpTo.value)
  // 必须为正整数，小数/非数字/0/负数一律跳过
  if (!Number.isInteger(n) || n < 1) return
  goToPage(n)
}

watch(viewMode, (mode) => {
  localStorage.setItem('viewMode', mode)
  if (!pageSizes.value.includes(pageSize.value)) {
    pageSize.value = pageSizes.value[0]
    localStorage.setItem('pageSize', pageSize.value)
  }
  currentPage.value = 1
})

watch(keyword, () => {
  currentPage.value = 1
})

watch(pageSize, (size) => {
  localStorage.setItem('pageSize', size)
  currentPage.value = 1
})

function enterSelectMode() {
  selectMode.value = true
}

function exitSelectMode() {
  selectMode.value = false
  selectedIds.value = new Set()
}

function toggleSelect(id) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  selectedIds.value = new Set(selectedIds.value)
}

function toggleSelectAll(checked) {
  if (checked) {
    filteredBirthdays.value.forEach(b => selectedIds.value.add(b.id))
  } else {
    selectedIds.value.clear()
  }
  selectedIds.value = new Set(selectedIds.value)
}

function handleKeydown(e) {
  if (e.key === 'Escape' && selectMode.value) {
    exitSelectMode()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

async function loadData() {
  try {
    const [all, up] = await Promise.all([
      listBirthdays(),
      listUpcoming(30),
    ])
    birthdays.value = all
    upcoming.value = up
    currentPage.value = 1
  } catch (e) {
    console.error('Load failed:', e)
  }
}

function openAddModal() {
  selectedBirthday.value = null
  modalShow.value = true
}

function openEditModal(birthday) {
  selectedBirthday.value = birthday
  modalShow.value = true
}

async function handleSave(data) {
  try {
    if (data.id) {
      await updateBirthday(data.id, data)
    } else {
      await createBirthday(data)
    }
    modalShow.value = false
    loadData()
  } catch (e) {
    console.error('Save failed:', e)
  }
}

function handleDelete(id, name) {
  confirmIds.value = [id]
  confirmNames.value = [name]
  confirmShow.value = true
}

function openBatchDelete() {
  const ids = Array.from(selectedIds.value)
  const names = filteredBirthdays.value
    .filter(b => selectedIds.value.has(b.id))
    .map(b => b.name)
  confirmIds.value = ids
  confirmNames.value = names
  confirmShow.value = true
}

async function confirmDelete() {
  try {
    await Promise.all(confirmIds.value.map(id => deleteBirthday(id)))
    confirmShow.value = false
    exitSelectMode()
    loadData()
  } catch (e) {
    console.error('Delete failed:', e)
  }
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
