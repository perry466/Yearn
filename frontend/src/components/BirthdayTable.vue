<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
    <table class="w-full">
      <thead>
        <tr class="border-b border-gray-100 dark:border-gray-700">
          <th v-if="selectMode" class="w-10 px-4 py-3">
            <input
              type="checkbox"
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              @change="$emit('toggle-all', $event.target.checked)"
              class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500 cursor-pointer"
            />
          </th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider" :class="selectMode ? 'pl-2' : ''">{{ t('form.name') }}</th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider hidden sm:table-cell">{{ t('form.category') }}</th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ t('form.solarDate') }}</th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider hidden md:table-cell">{{ lang === 'zh' ? '今年日期' : 'This Year' }}</th>
          <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ lang === 'zh' ? '倒计时' : 'Countdown' }}</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ lang === 'zh' ? '操作' : 'Actions' }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-50 dark:divide-gray-700">
        <tr
          v-for="b in birthdays"
          :key="b.id"
          class="transition-colors"
          :class="[
            selectedIds.has(b.id) ? 'bg-primary-50 dark:bg-primary-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-700/50',
            selectMode ? 'cursor-pointer' : 'cursor-pointer'
          ]"
          @click="selectMode ? $emit('toggle-select', b.id) : $emit('edit', b)"
        >
          <td v-if="selectMode" class="px-4 py-3" @click.stop>
            <input
              type="checkbox"
              :checked="selectedIds.has(b.id)"
              @change="$emit('toggle-select', b.id)"
              class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500 cursor-pointer"
            />
          </td>

          <td class="px-4 py-3" :class="selectMode ? 'pl-2' : ''">
            <div class="flex items-center gap-3">
              <div
                class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                :style="{ background: getGradient(b.name) }"
              >
                {{ b.name.charAt(0).toUpperCase() }}
              </div>
              <span class="font-medium text-gray-800 dark:text-white">{{ b.name }}</span>
            </div>
          </td>

          <td class="px-4 py-3 hidden sm:table-cell">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              {{ b.category ? t('form.categories.' + categoryKey(b.category)) : '' }}
            </span>
          </td>

          <td class="px-4 py-3">
            <span class="text-sm text-gray-600 dark:text-gray-300">
              {{ b.is_lunar ? (lang === 'zh' ? '农历' : 'Lunar') : (lang === 'zh' ? '公历' : 'Solar') }} {{ b.is_lunar ? b.lunar_date : b.solar_date }}
            </span>
          </td>

          <td class="px-4 py-3 hidden md:table-cell">
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ b.upcoming_date || '-' }}</span>
          </td>

          <td class="px-4 py-3 text-center">
            <span
              v-if="b.days_until !== null"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold"
              :class="getDaysClass(b.days_until)"
            >
              {{ b.days_until === 0 ? t('home.today') : b.days_until + (lang === 'zh' ? '天' : 'd') }}
            </span>
            <span v-else class="text-xs text-gray-400">-</span>
          </td>

          <td class="px-4 py-3 text-right" @click.stop>
            <div class="flex items-center justify-end gap-1">
              <button
                v-if="!selectMode"
                @click="$emit('edit', b)"
                class="p-1.5 rounded-lg text-gray-400 hover:text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/30 transition-colors text-sm"
                :title="t('common.edit')"
              >
                ✏️
              </button>
              <button
                v-if="!selectMode"
                @click="$emit('delete', b.id, b.name)"
                class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors text-sm"
                :title="t('common.delete')"
              >
                🗑️
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="birthdays.length === 0" class="text-center py-16">
      <p class="text-5xl mb-4">🎂</p>
      <p class="text-gray-400 dark:text-gray-500">{{ lang === 'zh' ? '还没有记录，添加一个吧' : 'No records yet — add one!' }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t, lang } = useI18n()

const props = defineProps({
  birthdays: { type: Array, default: () => [] },
  selectMode: { type: Boolean, default: false },
  selectedIds: { type: Set, default: () => new Set() },
})

defineEmits(['edit', 'delete', 'toggle-select', 'toggle-all'])

const categoryMap = { '朋友': 'friend', '家人': 'family', '同事': 'colleague', '客户': 'client', '同学': 'classmate', '其他': 'other' }
function categoryKey(cat) {
  return categoryMap[cat] || cat
}

const isAllSelected = computed(() =>
  props.birthdays.length > 0 && props.birthdays.every(b => props.selectedIds.has(b.id))
)

const isIndeterminate = computed(() =>
  !isAllSelected.value && props.birthdays.some(b => props.selectedIds.has(b.id))
)

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

function getGradient(name) {
  return gradients[name.charCodeAt(0) % gradients.length]
}

function getDaysClass(days) {
  if (days === 0) return 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400'
  if (days <= 1) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400'
  if (days <= 7) return 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400'
  if (days <= 15) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400'
  return 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
}
</script>
