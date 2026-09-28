<template>
  <div
    class="group relative bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border transition-all cursor-pointer"
    :class="selectMode
      ? selected
        ? 'border-primary-400 dark:border-primary-600 shadow-md ring-2 ring-primary-200 dark:ring-primary-800'
        : 'border-gray-200 dark:border-gray-700'
      : 'border-gray-100 dark:border-gray-700 hover:shadow-md hover:border-primary-200 dark:hover:border-primary-800'"
    @click="selectMode ? $emit('toggle-select') : $emit('edit', birthday)"
  >
    <!-- 复选框（选择模式下） -->
    <div
      v-if="selectMode"
      class="absolute top-3 right-3 z-10"
      @click.stop="$emit('toggle-select')"
    >
      <div
        class="w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all"
        :class="selected
          ? 'bg-primary-500 border-primary-500'
          : 'border-gray-300 dark:border-gray-600'"
      >
        <span v-if="selected" class="text-white text-xs font-bold">✓</span>
      </div>
    </div>

    <!-- 即将到来标记 -->
    <div v-if="birthday.days_until !== null && birthday.days_until <= 7" class="absolute -top-2 -left-2">
      <span
        class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold"
        :class="birthday.days_until === 0
          ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400'
          : birthday.days_until === 1
            ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400'
            : 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400'"
      >
        {{ birthday.days_until === 0 ? t('home.today') + '!' : tf('home.daysUntil', { days: birthday.days_until }) }}
      </span>
    </div>

    <!-- 头像/名字首字 -->
    <div class="flex items-center gap-3 mb-3">
      <div
        class="w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold text-white"
        :style="{ background: avatarGradient }"
      >
        {{ birthday.name.charAt(0).toUpperCase() }}
      </div>
      <div class="flex-1 min-w-0" :class="selectMode ? 'pr-6' : ''">
        <h3 class="font-bold text-gray-800 dark:text-white truncate">{{ birthday.name }}</h3>
        <p class="text-xs text-gray-400">{{ birthday.category ? t('form.categories.' + categoryKey(birthday.category)) : '' }}</p>
      </div>
    </div>

    <!-- 生日日期 -->
    <div class="space-y-1.5 mb-3">
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-400">🎂</span>
        <span class="text-gray-600 dark:text-gray-300">
          {{ birthday.is_lunar ? (lang === 'zh' ? '农历 ' : 'Lunar ') : (lang === 'zh' ? '公历 ' : 'Solar ') }}{{ birthday.is_lunar ? birthday.lunar_date : birthday.solar_date }}
        </span>
      </div>
      <div v-if="birthday.upcoming_date" class="flex items-center gap-2 text-sm">
        <span class="text-gray-400">📅</span>
        <span class="text-gray-600 dark:text-gray-300">
          {{ lang === 'zh' ? '今年 ' : 'This year: ' }}{{ birthday.upcoming_date }}
        </span>
      </div>
    </div>

    <!-- 备注 -->
    <p v-if="birthday.remark" class="text-xs text-gray-400 line-clamp-2 mb-3">
      {{ birthday.remark }}
    </p>

    <!-- 操作按钮（非选择模式时悬停显示） -->
    <div
      v-if="!selectMode"
      class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
      @click.stop
    >
      <button
        @click="$emit('edit', birthday)"
        class="p-2 rounded-lg text-gray-400 hover:text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/30 transition-colors"
        :title="t('common.edit')"
      >
        ✏️
      </button>
      <button
        @click="$emit('delete', birthday.id, birthday.name)"
        class="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
        :title="t('common.delete')"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t, tf, lang } = useI18n()

const categoryMap = { '朋友': 'friend', '家人': 'family', '同事': 'colleague', '客户': 'client', '同学': 'classmate', '其他': 'other' }
function categoryKey(cat) {
  return categoryMap[cat] || cat
}
const props = defineProps({
  birthday: { type: Object, required: true },
  selectMode: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
})

defineEmits(['edit', 'delete', 'toggle-select'])

const gradients = [
  'linear-gradient(135deg, #FF6B6B, #FFA07A)',
  'linear-gradient(135deg, #4ECDC4, #45B7D1)',
  'linear-gradient(135deg, #96CEB4, #88D8B0)',
  'linear-gradient(135deg, #DDA0DD, #DA70D6)',
  'linear-gradient(135deg, #87CEEB, #6495ED)',
  'linear-gradient(135deg, #F0E68C, #FFD700)',
  'linear-gradient(135deg, #FFB6C1, #FF69B4)',
  'linear-gradient(135deg, #98D8C8, #7FDBDA)',
]

const avatarGradient = computed(() => {
  const charCode = props.birthday.name.charCodeAt(0)
  return gradients[charCode % gradients.length]
})
</script>
