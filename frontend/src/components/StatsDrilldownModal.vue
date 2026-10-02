<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative ui-panel rounded-2xl shadow-xl w-full max-w-lg z-10 overflow-hidden flex flex-col max-h-[82vh]">
          <!-- 头部 -->
          <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100 dark:border-gray-700">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-xl flex-shrink-0"
              :style="{ background: color + '22' }"
            >
              {{ icon }}
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-gray-800 dark:text-white truncate">{{ title }}</h3>
              <p class="text-xs text-gray-400">
                {{ items.length }} {{ t('common.records') }}
              </p>
            </div>
            <button
              @click="$emit('close')"
              class="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex-shrink-0"
              :title="t('common.close')"
            >
              ✕
            </button>
          </div>

          <!-- 明细列表 -->
          <div class="overflow-y-auto px-2 py-2">
            <div v-if="items.length === 0" class="text-center py-14">
              <p class="text-4xl mb-3">🎂</p>
              <p class="text-gray-400 dark:text-gray-500">{{ t('common.noData') }}</p>
            </div>

            <div
              v-for="b in items"
              :key="b.id"
              class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <!-- 性别头像 -->
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center text-xl flex-shrink-0"
                :class="avatarBg(b.gender)"
              >
                {{ avatarEmoji(b.gender) }}
              </div>

              <!-- 姓名 + 分类 + 日期 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-gray-800 dark:text-white truncate">{{ b.name }}</span>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full flex-shrink-0"
                    :style="{ background: categoryColor(b.category) + '22', color: categoryColor(b.category) }"
                  >
                    {{ t('form.categories.' + (b.category || 'other')) }}
                  </span>
                </div>
                <div class="text-xs text-gray-400 mt-0.5 truncate">
                  <span v-if="b.age !== null && b.age !== undefined">{{ b.age }}{{ lang === 'zh' ? '岁' : ' yrs' }} · </span>
                  {{ b.is_lunar ? (lang === 'zh' ? '农历 ' : 'Lunar ') : (lang === 'zh' ? '公历 ' : 'Solar ') }}{{ dateStr(b) }}
                </div>
              </div>

              <!-- 倒计时 -->
              <div v-if="b.days_until !== null && b.days_until !== undefined" class="text-right flex-shrink-0">
                <div class="text-sm font-bold" :style="{ color: daysColor(b.days_until) }">
                  {{ b.days_until === 0 ? t('home.today') : tf('home.daysUntil', { days: b.days_until }) }}
                </div>
                <div class="text-xs text-gray-400">{{ b.upcoming_date }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { useI18n } from '../composables/useI18n'

const { t, tf, lang } = useI18n()

defineProps({
  show: Boolean,
  title: { type: String, default: '' },
  icon: { type: String, default: '📂' },
  color: { type: String, default: '#f97316' },
  items: { type: Array, default: () => [] },
})
defineEmits(['close'])

const GENDER_CONFIG = {
  male:        { emoji: '👦', bg: 'bg-blue-100 dark:bg-blue-900/40' },
  female:      { emoji: '👧', bg: 'bg-pink-100 dark:bg-pink-900/40' },
  unspecified: { emoji: '😊', bg: 'bg-gray-100 dark:bg-gray-700' },
}

const CATEGORY_COLORS = {
  '朋友': '#FF6B6B',
  '家人': '#4ECDC4',
  '同事': '#96CEB4',
  '客户': '#DDA0DD',
  '同学': '#87CEEB',
  'other': '#F0E68C',
}

function avatarConfig(gender) {
  return GENDER_CONFIG[gender] || GENDER_CONFIG.unspecified
}
function avatarEmoji(gender) {
  return avatarConfig(gender).emoji
}
function avatarBg(gender) {
  return avatarConfig(gender).bg
}

function categoryColor(cat) {
  return CATEGORY_COLORS[cat] || '#9CA3AF'
}

function dateStr(b) {
  if (b.is_lunar && b.lunar_date) return b.lunar_date.replace('-leap', '')
  return b.solar_date
}

function daysColor(days) {
  if (days === 0) return '#ef4444'
  if (days === 1) return '#f97316'
  if (days <= 7) return '#f59e0b'
  return '#9CA3AF'
}
</script>
