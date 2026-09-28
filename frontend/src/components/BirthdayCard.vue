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

    <!-- 头像 + 姓名 + 年龄性别 -->
    <div class="flex items-center gap-3 mb-3">
      <!-- 性别头像 -->
      <div
        class="w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
        :class="avatarBgClass"
      >
        {{ avatarEmoji }}
      </div>
      <div class="flex-1 min-w-0" :class="selectMode ? 'pr-6' : ''">
        <h3 class="font-bold text-gray-800 dark:text-white truncate">{{ birthday.name }}</h3>
        <p class="text-xs text-gray-400">
          <span v-if="birthday.age !== null && birthday.age !== undefined">
            {{ birthday.age }}{{ lang === 'zh' ? '岁' : ' yrs' }}
            <span class="ml-1">{{ ageGenderSymbol }}</span>
          </span>
          <span v-else>{{ birthday.category ? t('form.categories.' + categoryKey(birthday.category)) : '' }}</span>
        </p>
      </div>
    </div>

    <!-- 生日日期 -->
    <div class="space-y-1.5 mb-3">
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-400">🎂</span>
        <span class="text-gray-600 dark:text-gray-300">
          {{ birthday.is_lunar ? (lang === 'zh' ? '农历 ' : 'Lunar ') : (lang === 'zh' ? '公历 ' : 'Solar ') }}{{ birthday.is_lunar ? birthday.lunar_date.replace('-leap','') : birthday.solar_date }}
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

function categoryKey(cat) {
  return cat
}

const props = defineProps({
  birthday: { type: Object, required: true },
  selectMode: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
})

defineEmits(['edit', 'delete', 'toggle-select'])

const GENDER_CONFIG = {
  male:       { emoji: '👦', bg: 'bg-blue-100 dark:bg-blue-900/40' },
  female:     { emoji: '👧', bg: 'bg-pink-100 dark:bg-pink-900/40' },
  unspecified:{ emoji: '😊', bg: 'bg-gray-100 dark:bg-gray-700' },
}

const avatarConfig = computed(() => {
  return GENDER_CONFIG[props.birthday.gender] || GENDER_CONFIG.unspecified
})

const avatarEmoji = computed(() => avatarConfig.value.emoji)
const avatarBgClass = computed(() => avatarConfig.value.bg)

const ageGenderSymbol = computed(() => {
  const g = props.birthday.gender
  if (g === 'male') return '♂'
  if (g === 'female') return '♀'
  return ''
})
</script>
