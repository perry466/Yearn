<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('cancel')" />

        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-sm z-10 overflow-hidden">
          <div class="bg-red-50 dark:bg-red-900/20 px-6 py-4 flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center text-xl">
              🗑️
            </div>
            <div>
              <h3 class="font-bold text-red-600 dark:text-red-400">
                {{ lang === 'zh' ? '确认删除' : 'Confirm Delete' }}
              </h3>
              <p class="text-sm text-red-400 dark:text-red-500">{{ t('home.deleteWarning') }}</p>
            </div>
          </div>

          <div class="px-6 py-4">
            <p class="text-gray-600 dark:text-gray-300">
              {{ tf('home.deleteConfirmTitle', { count: names.length }) }}
            </p>

            <div v-if="names.length > 1" class="mt-3 max-h-36 overflow-y-auto bg-gray-50 dark:bg-gray-700/50 rounded-lg px-3 py-2">
              <p
                v-for="(name, i) in names.slice(0, 10)"
                :key="i"
                class="text-sm text-gray-600 dark:text-gray-300 py-0.5"
              >
                {{ name }}
              </p>
              <p v-if="names.length > 10" class="text-sm text-gray-400 mt-1">
                {{ lang === 'zh' ? '...还有 ' : '...and ' }}{{ names.length - 10 }} {{ lang === 'zh' ? ' 条' : ' more' }}
              </p>
            </div>
          </div>

          <div class="px-6 pb-5 flex gap-3">
            <button
              @click="$emit('cancel')"
              class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="$emit('confirm')"
              class="flex-1 px-4 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 text-white font-medium transition-colors flex items-center justify-center gap-2"
            >
              <span>🗑️</span>
              <span>{{ t('common.confirm') }}</span>
            </button>
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
  names: { type: Array, default: () => [] },
})
defineEmits(['confirm', 'cancel'])
</script>
