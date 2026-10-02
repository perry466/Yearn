import { ref, reactive, computed, watch } from 'vue'
import { ACCENT_PRESETS } from '../theme/presets'
import {
  putBgBlob,
  getBgBlob,
  delBgBlob,
  fileToImage,
  imageToBlob,
  imageToDataUrl,
} from '../utils/bgImage'

// 主题状态（单例）：颜色模式 + 主题色 + 自定义背景（浅色/深色各一套）
// 持久化到 localStorage: 'yearn.theme'（JSON）
const STORAGE_KEY = 'yearn.theme'
const ACCENT_IDS = ACCENT_PRESETS.map((p) => p.id)

export function defaultBackground() {
  return {
    type: 'none', // none | color | gradient | image
    color: '#ffffff',
    from: '#ffedd5',
    to: '#fed7aa',
    angle: 135,
    url: '', // 外链图片地址
    fit: 'cover', // cover | contain（仅图片：铺满 / 完整显示）
    blur: 0, // px
    dim: 0.15, // 0~1 蒙版不透明度
    // 本地上传的图片：原图存入 IndexedDB（localStorage 装不下高分辨率图）
    stored: false, // true = 使用 IndexedDB 里的原图
    ph: '', // 首帧占位小图（dataURL，几 KB）
    w: 0, // 源图原始像素宽度（用于清晰度诊断）
    h: 0, // 源图原始像素高度
  }
}

const SCHEMA_VERSION = 2

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

// —— 本地上传图：原图存 IndexedDB，运行时用 blob URL 引用（不写进 localStorage）——
const objectUrls = { light: '', dark: '' }
// 长边超过该值才降采样（避免解码爆内存）；以内一律原图直存、零重编码
const MAX_STORED_EDGE = 4096

// 当前实际用于渲染的背景图地址（本地上传优先用 blob URL，回退占位图；否则用外链）
function resolveBgUrl(mode) {
  const bg = state.background[mode]
  if (!bg || bg.type !== 'image') return ''
  if (bg.stored) return objectUrls[mode] || bg.ph || ''
  return bg.url || ''
}

// 启动时把 IndexedDB 里的原图取回，生成 blob URL 并重绘
async function refreshStoredImages() {
  let changed = false
  for (const mode of ['light', 'dark']) {
    const bg = state.background[mode]
    if (!bg || !bg.stored) continue
    try {
      const blob = await getBgBlob(mode)
      if (blob) {
        if (objectUrls[mode]) URL.revokeObjectURL(objectUrls[mode])
        objectUrls[mode] = URL.createObjectURL(blob)
        changed = true
      }
    } catch (e) {
      console.warn('[theme] 读取本地背景原图失败：', e)
    }
  }
  if (changed) applyBackground()
}

// 保存本地上传的图片：优先原图直存（保画质），仅超大图降采样
async function setImageFile(mode, file) {
  const img = await fileToImage(file)
  const long = Math.max(img.naturalWidth, img.naturalHeight)
  const blob = long > MAX_STORED_EDGE ? await imageToBlob(img, MAX_STORED_EDGE, 0.92) : file
  const ph = imageToDataUrl(img, 48, 0.6)
  await putBgBlob(mode, blob)
  if (objectUrls[mode]) URL.revokeObjectURL(objectUrls[mode])
  objectUrls[mode] = URL.createObjectURL(blob)
  const bg = state.background[mode]
  bg.type = 'image'
  bg.stored = true
  bg.ph = ph
  bg.url = ''
  bg.w = img.naturalWidth
  bg.h = img.naturalHeight
  applyBackground()
  return persist()
}

async function clearStoredImage(mode) {
  const bg = state.background[mode]
  if (objectUrls[mode]) {
    URL.revokeObjectURL(objectUrls[mode])
    objectUrls[mode] = ''
  }
  bg.stored = false
  bg.ph = ''
  bg.w = 0
  bg.h = 0
  try {
    await delBgBlob(mode)
  } catch (e) {
    console.warn('[theme] 清除本地背景原图失败：', e)
  }
}

// 用户填写外链地址：改用外链，并清掉本地上传的原图
function setImageUrl(mode, url) {
  const bg = state.background[mode]
  bg.url = url
  if (!url) return
  bg.type = 'image'
  if (bg.stored) clearStoredImage(mode)
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    return true
  } catch (e) {
    // 多为图片过大导致超出配额；本地上传图已改存 IndexedDB，这里仅兜底外链/占位图
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
  // 铺满 / 完整（仅图片有意义；渐变与纯色无固有尺寸，统一 cover 填满）
  root.style.setProperty(
    '--bg-size',
    bg.type === 'image' && bg.fit === 'contain' ? 'contain' : 'cover',
  )
  const blur = bg.blur || 0
  if (blur > 0) {
    root.style.setProperty('--bg-filter', `blur(${blur}px)`)
    root.style.setProperty('--bg-scale', '1.08')
  } else {
    // 不虚化时完全去掉滤镜层，避免图片被重栅格化而发虚
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
    refreshStoredImages()
    watch(
      state,
      () => {
        applyAll()
        persist()
      },
      { deep: true },
    )
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
