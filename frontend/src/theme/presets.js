// 主题预设：主题色（accent）与内置渐变背景（gradient）。
// 注意：主题色的完整 50~900 色阶定义在 src/assets/main.css 的 .accent-* 类里，
// 这里只保留 id / 名称 / 代表色，用于渲染色板按钮，避免 CSS 与 JS 双份维护色阶。

export const ACCENT_PRESETS = [
  { id: 'orange', color: '#F97316', name: { zh: '活力橙', en: 'Sunset' } },
  { id: 'pink', color: '#EC4899', name: { zh: '樱花粉', en: 'Sakura' } },
  { id: 'sky', color: '#0EA5E9', name: { zh: '静谧蓝', en: 'Calm Blue' } },
  { id: 'emerald', color: '#10B981', name: { zh: '森林绿', en: 'Forest' } },
  { id: 'violet', color: '#8B5CF6', name: { zh: '紫罗兰', en: 'Violet' } },
  { id: 'slate', color: '#64748B', name: { zh: '石墨灰', en: 'Graphite' } },
]

// 内置渐变背景：纯 CSS 渐变，零资源依赖、离线可用，深浅模式都兼顾。
export const GRADIENT_PRESETS = [
  { id: 'sunrise', name: { zh: '暖阳', en: 'Sunrise' }, from: '#ffecd2', to: '#fcb69f', angle: 135 },
  { id: 'sakura', name: { zh: '樱花', en: 'Sakura' }, from: '#ffe4e6', to: '#fbcfe8', angle: 135 },
  { id: 'sky', name: { zh: '晴空', en: 'Clear Sky' }, from: '#e0f2fe', to: '#bae6fd', angle: 135 },
  { id: 'mint', name: { zh: '薄荷', en: 'Mint' }, from: '#d1fae5', to: '#a7f3d0', angle: 135 },
  { id: 'lavender', name: { zh: '薰衣草', en: 'Lavender' }, from: '#ede9fe', to: '#ddd6fe', angle: 135 },
  { id: 'cream', name: { zh: '奶油', en: 'Cream' }, from: '#fdf6e3', to: '#f5e6c8', angle: 160 },
  { id: 'dusk', name: { zh: '暮色', en: 'Dusk' }, from: '#1e293b', to: '#334155', angle: 135 },
  { id: 'deepsea', name: { zh: '深海', en: 'Deep Sea' }, from: '#0f172a', to: '#1e3a8a', angle: 135 },
]

export const BACKGROUND_TYPES = ['none', 'color', 'gradient', 'image']

// 由 from/to/angle 生成 linear-gradient 字符串
export function gradientCss({ from, to, angle }) {
  return `linear-gradient(${angle != null ? angle : 135}deg, ${from || '#ffffff'}, ${to || '#dddddd'})`
}
