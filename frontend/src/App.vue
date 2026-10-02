<template>
  <div>
    <!-- 自定义背景层（未启用时由 CSS 隐藏） -->
    <div class="app-background" aria-hidden="true"></div>

    <div class="relative z-10 min-h-screen transition-colors">
      <!-- 顶部导航 -->
      <nav class="sticky top-0 z-50 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
        <div class="max-w-6xl mx-auto px-4">
          <div class="flex items-center justify-between h-16">
            <!-- Logo -->
            <div class="flex items-center gap-2">
              <span class="text-2xl">🎂</span>
              <span class="font-bold text-lg text-gray-800 dark:text-white">{{ t('app.title') }}</span>
            </div>

            <!-- 导航链接 -->
            <div class="flex items-center gap-1">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="$route.path === item.path
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                {{ item.icon }} {{ t(item.labelKey) }}
              </router-link>

              <!-- 语言切换 -->
              <button
                @click="toggleLang()"
                class="ml-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                :title="lang === 'zh' ? 'Switch to English' : '切换到中文'"
              >
                {{ lang === 'zh' ? 'EN' : '中' }}
              </button>

              <!-- 暗色模式切换 -->
              <button
                @click="toggleDark()"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                :title="isDark ? t('common.light') : t('common.dark')"
              >
                {{ isDark ? '☀️' : '🌙' }}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- 页面内容 -->
      <main class="max-w-7xl mx-auto px-4 py-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from './composables/useI18n'
import { useTheme } from './composables/useTheme'

const { t, lang, toggleLang } = useI18n()
const { isDark, setMode } = useTheme()

const navItems = [
  { path: '/', labelKey: 'nav.home', icon: '🏠' },
  { path: '/calendar', labelKey: 'nav.calendar', icon: '📅' },
  { path: '/stats', labelKey: 'nav.stats', icon: '📊' },
  { path: '/settings', labelKey: 'nav.settings', icon: '⚙️' },
]

// 顶部按钮：在浅色/深色之间切换（若当前是「跟随系统」，则切到当前的反面）
function toggleDark() {
  setMode(isDark.value ? 'light' : 'dark')
}
</script>
