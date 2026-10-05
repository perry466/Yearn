import { ref, reactive, computed, watch } from 'vue'
import { ACCENT_PRESETS } from '../theme/presets'
import {
  uploadBlob,
  imageUrl,
  deleteImage,
  getBgBlob, // 仅一次性迁移用
  delBgBlob, // 仅一次性迁移用
  fileToImage,
  imageToBlob,
  imageToDataUrl,
} from '../utils/bgImage'

// 主题状态（单例）：颜色模式 + 主题色 + 自定义背景（浅色/深色各一套）
// 真源在「后端」（/api/theme），localStorage 'yearn.theme' 仅作首帧镜像/离线兜底。
const STORAGE_KEY = 'yearn.theme'
const MIGRATED_KEY = 'yearn.theme.migrated' // 标记旧 IndexedDB 是否已迁到后端
const ACCENT_IDS = ACCENT_PRESETS.map((p) => p.id)

export function defaultBackground() {
  return {
    type: 'none', // none | color | gradient | image
    color: '#ffffff',
    from: '#ffedd5',
    to: '#fed7aa',
    angle: 135,
    url: '', // 外链图片地址 / 后端图片地址（stored 时）
    fit: 'cover', // cover | contain（仅图片：铺满 / 完整显示）
    blur: 0, // px
    dim: 0.15, // 0~1 蒙版不透明度
    // 本地上传的图片：存到后端（DATA_DIR/images/），所有浏览器共享同一张
    stored: false, // true = 使用后端图片
    imageId: 0, // 后端图片 id（stored 时有效）
    ph: '', // 兼容旧版（已不再使用，留空）
    w: 0, // 源图原始像素宽度（用于清晰度诊断）
    h: 0, // 源图原始像素高度
  }
}

const SCHEMA_VERSION = 2
// 本地上传图：仅超大图降采样（避免解码爆内存）；以内一律原图直存、零重编码
const MAX_STORED_EDGE = 4096

function loadState() {
  let saved = {}
  try {
    saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') || {}
  } catch (e) {
    saved = {}
  }
  // 兼容旧版：此前只存了 theme = 'dark' | 'light'
  const legacy = localStorage.getItem('theme')
  const mode =
    saved.mode || (legacy === 'dark' ? 'dark' : legacy === 'light' ? 'light' : 'system')
  // v1 时代「虚化」可能残留非零值，升级时统一清零，避免背景无端发虚
  const background = {
    light: { ...defaultBackground(), ...(saved.background && saved.background.light) },
    dark: { ...defaultBackground(), ...(saved.background && saved.background.dark) },
  }
  if ((saved.v || 0) < SCHEMA_VERSION) {
    background.light.blur = 0
    background.dark.blur = 0
  }
  // 界面面板不透明度（0.4~1），由「外观」滑块控制
  const uiAlpha = Math.min(1, Math.max(0.4, Number(saved.uiAlpha) || 1))
  return {
    v: SCHEMA_VERSION,
    mode,
    accent: ACCENT_IDS.includes(saved.accent) ? saved.accent : 'orange',
    uiAlpha,
    background,
  }
}

const state = reactive(loadState())

const systemDark = ref(
  typeof window !== 'undefined' && window.matchMedia
    ? window.matchMedia('(prefers-color-scheme: dark)').matches
    : false,
)

if (typeof window !== 'undefined' && window.matchMedia) {
  const mql = window.matchMedia('(prefers-color-scheme: dark)')
  const onChange = (e) => {
    systemDark.value = e.matches
    if (state.mode === 'system') applyAll()
  }
  if (mql.addEventListener) mql.addEventListener('change', onChange)
  else if (mql.addListener) mql.addListener(onChange)
}

const isDark = computed(
  () => state.mode === 'dark' || (state.mode === 'system' && systemDark.value),
)

// 当前生效的背景配置（跟随浅色/深色）
const activeBackground = computed(() => state.background[isDark.value ? 'dark' : 'light'])

const hasCustomBackground = computed(
  () => !!activeBackground.value && activeBackground.value.type !== 'none',
)

// 当前实际用于渲染的背景图地址（后端图片或外链）
function resolveBgUrl(mode) {
  const bg = state.background[mode]
  if (!bg || bg.type !== 'image') return ''
  return bg.url || ''
}

// ============ 与后端同步 ============
// localStorage 镜像（持久化用，scheme 与后端一致）
function buildServerPayload() {
  return {
    v: state.v,
    mode: state.mode,
    accent: state.accent,
    uiAlpha: state.uiAlpha,
    background: {
      light: { ...state.background.light },
      dark: { ...state.background.dark },
    },
  }
}

// 改动后回写服务器（防抖，避免滑块拖动刷屏）
let putTimer = null
function schedulePutServer() {
  if (putTimer) clearTimeout(putTimer)
  putTimer = setTimeout(() => {
    putTimer = null
    fetch('/api/theme', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: buildServerPayload() }),
    }).catch((e) => console.warn('[theme] 保存到服务器失败：', e))
  }, 400)
}

async function fetchServerTheme() {
  try {
    const r = await fetch('/api/theme')
    if (!r.ok) return null
    const j = await r.json()
    return j.data || null
  } catch (e) {
    return null
  }
}

// 一次性迁移：把旧 IndexedDB 里的原图上传到后端，并把本地设置整包 PUT 到服务器
async function migrateLegacyToServer() {
  if (localStorage.getItem(MIGRATED_KEY) === '1') return
  const bg = state.background
  const hasLegacy =
    bg.light.stored ||
    bg.dark.stored ||
    state.mode !== 'system' ||
    state.accent !== 'orange' ||
    state.uiAlpha !== 1
  if (!hasLegacy) {
    localStorage.setItem(MIGRATED_KEY, '1')
    return
  }
  for (const mode of ['light', 'dark']) {
    const b = bg[mode]
    if (b && b.stored) {
      try {
        const blob = await getBgBlob(mode)
        if (blob) {
          const id = await uploadBlob(blob)
          b.imageId = id
          b.url = imageUrl(id)
          await delBgBlob(mode) // 迁移完成，清掉旧 IndexedDB 原图
        }
      } catch (e) {
        console.warn('[theme] 迁移本地背景失败：', e)
      }
    }
  }
  await fetch('/api/theme', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: buildServerPayload() }),
  }).catch((e) => console.warn('[theme] 迁移到服务器失败：', e))
  localStorage.setItem(MIGRATED_KEY, '1')
}

// 启动后从服务器拉取（跨浏览器跟随同一设置；若服务器为空则迁移本地旧数据）
async function reconcileWithServer() {
  const server = await fetchServerTheme()
  if (server) {
    // 服务器为真源：覆盖本地并写回镜像
    state.mode = server.mode || state.mode
    state.accent = ACCENT_IDS.includes(server.accent) ? server.accent : state.accent
    state.uiAlpha = Math.min(1, Math.max(0.4, Number(server.uiAlpha) || 1))
    if (server.background && server.background.light) {
      state.background.light = { ...defaultBackground(), ...server.background.light }
    }
    if (server.background && server.background.dark) {
      state.background.dark = { ...defaultBackground(), ...server.background.dark }
    }
    applyAll()
    persist()
    return
  }
  // 服务器为空 → 迁移本地旧数据（仅首次）
  await migrateLegacyToServer()
}

// ============ 本地上传图：原图直存后端（不再走 IndexedDB）============
async function setImageFile(mode, file) {
  const img = await fileToImage(file)
  const long = Math.max(img.naturalWidth, img.naturalHeight)
  const blob = long > MAX_STORED_EDGE ? await imageToBlob(img, MAX_STORED_EDGE, 0.92) : file
  const id = await uploadBlob(blob)
  const bg = state.background[mode]
  bg.type = 'image'
  bg.stored = true
  bg.imageId = id
  bg.url = imageUrl(id)
  bg.ph = ''
  bg.w = img.naturalWidth
  bg.h = img.naturalHeight
  applyBackground()
  return persist() // 镜像写回 localStorage；deep watch 会再回写服务器
}

async function clearStoredImage(mode) {
  const bg = state.background[mode]
  if (bg.imageId) {
    await deleteImage(bg.imageId)
    bg.imageId = 0
  }
  bg.stored = false
  bg.url = ''
  bg.ph = ''
  bg.w = 0
  bg.h = 0
}

// 用户填写外链地址：改用外链，并清掉后端图片
function setImageUrl(mode, url) {
  const bg = state.background[mode]
  bg.url = url
  bg.stored = false
  bg.imageId = 0
  bg.ph = ''
  if (!url) return
  bg.type = 'image'
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    return true
  } catch (e) {
    console.warn('[theme] 保存失败：', e)
    return false
  }
}

function applyMode() {
  document.documentElement.classList.toggle('dark', isDark.value)
  // 同步旧键，保持向后兼容
  try {
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  } catch (e) {}
}

function applyAccent() {
  const root = document.documentElement
  ACCENT_IDS.forEach((id) => root.classList.remove('accent-' + id))
  root.classList.add('accent-' + state.accent)
}

function applyBackground() {
  const root = document.documentElement
  const bg = activeBackground.value
  if (!bg || bg.type === 'none') {
    root.classList.remove('has-custom-bg')
    root.style.removeProperty('--bg-color')
    root.style.removeProperty('--bg-image')
    root.style.removeProperty('--bg-size')
    root.style.removeProperty('--bg-filter')
    root.style.removeProperty('--bg-scale')
    root.style.removeProperty('--bg-dim-alpha')
    return
  }
  root.classList.add('has-custom-bg')
  root.style.setProperty(
    '--bg-size',
    bg.type === 'image' && bg.fit === 'contain' ? 'contain' : 'cover',
  )
  const blur = bg.blur || 0
  if (blur > 0) {
    root.style.setProperty('--bg-filter', `blur(${blur}px)`)
    root.style.setProperty('--bg-scale', '1.08')
  } else {
    root.style.removeProperty('--bg-filter')
    root.style.setProperty('--bg-scale', '1')
  }
  root.style.setProperty('--bg-dim-alpha', String(bg.dim != null ? bg.dim : 0.15))
  if (bg.type === 'color') {
    root.style.setProperty('--bg-color', bg.color || 'transparent')
    root.style.setProperty('--bg-image', 'none')
  } else if (bg.type === 'gradient') {
    root.style.setProperty('--bg-color', bg.from || '#ffffff')
    root.style.setProperty(
      '--bg-image',
      `linear-gradient(${bg.angle != null ? bg.angle : 135}deg, ${bg.from || '#ffffff'}, ${bg.to || '#dddddd'})`,
    )
  } else if (bg.type === 'image') {
    root.style.setProperty('--bg-color', '#f3f4f6')
    const imgUrl = resolveBgUrl(isDark.value ? 'dark' : 'light')
    root.style.setProperty('--bg-image', imgUrl ? `url("${imgUrl}")` : 'none')
  }
}

function applyAll() {
  applyMode()
  applyAccent()
  applyBackground()
  applyUiAlpha()
}

// 界面面板不透明度（卡片/分区/弹窗等主面板），拖动滑块即可让壁纸透出或挡住
function applyUiAlpha() {
  document.documentElement.style.setProperty(
    '--ui-alpha',
    String(state.uiAlpha != null ? state.uiAlpha : 1),
  )
}

let started = false

export function useTheme() {
  if (!started && typeof document !== 'undefined') {
    started = true
    applyAll()
    watch(
      state,
      () => {
        applyAll()
        persist()
        schedulePutServer()
      },
      { deep: true },
    )
    // 启动后与服务器对账（拉取最新 / 必要时迁移旧数据）
    reconcileWithServer()
  }

  return {
    state,
    isDark,
    activeBackground,
    hasCustomBackground,
    applyAll,
    resolveBgUrl,
    setImageFile,
    setImageUrl,
    saveNow() {
      return persist()
    },
    setMode(mode) {
      state.mode = mode
    },
    setAccent(accent) {
      if (ACCENT_IDS.includes(accent)) state.accent = accent
    },
  }
}
