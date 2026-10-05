// 背景图存储：本地上传改为存后端（DATA_DIR/images/），跨浏览器 / 跨设备跟随同一服务。
//
// - 新流程：uploadBlob() 上传到 /api/theme/image，imageUrl() 取展示地址，deleteImage() 删除。
// - 一次性迁移：getBgBlob() / delBgBlob() 仅用于把旧 IndexedDB（yearn-bg）里的原图迁到后端，
//   迁移完成后 IndexedDB 不再被使用。

// ============ 旧 IndexedDB（仅迁移用，可保留）============
const DB_NAME = 'yearn-bg'
const STORE = 'images'
const VERSION = 1

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE)
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function withStore(fn) {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const t = db.transaction(STORE, 'readwrite')
    let out
    const req = fn(t.objectStore(STORE))
    if (req) req.onsuccess = () => { out = req.result }
    t.oncomplete = () => resolve(out)
    t.onerror = () => reject(t.error)
    t.onabort = () => reject(t.error)
  })
}

// 仅迁移用：把旧 IndexedDB 里的原图取回 / 删除
export const getBgBlob = (mode) => withStore((s) => s.get(mode))
export const delBgBlob = (mode) => withStore((s) => s.delete(mode))

// ============ 后端 API（主路径）============
export async function uploadBlob(blob) {
  const fd = new FormData()
  fd.append('file', blob, 'bg.jpg')
  const r = await fetch('/api/theme/image', { method: 'POST', body: fd })
  if (!r.ok) throw new Error('upload failed: ' + r.status)
  const j = await r.json()
  return j.id
}

export function imageUrl(id) {
  return `/api/theme/image/${id}`
}

export async function deleteImage(id) {
  if (!id) return
  try {
    await fetch(`/api/theme/image/${id}`, { method: 'DELETE' })
  } catch (e) {
    console.warn('[theme] 删除服务器背景图失败：', e)
  }
}

// ============ 解码 / 降采样辅助（上传前处理，保持画质）============
export function fileToImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('image decode failed'))
    }
    img.src = url
  })
}

function drawToCanvas(img, maxEdge) {
  const long = Math.max(img.naturalWidth, img.naturalHeight)
  const ratio = maxEdge && long > maxEdge ? maxEdge / long : 1
  const w = Math.max(1, Math.round(img.naturalWidth * ratio))
  const h = Math.max(1, Math.round(img.naturalHeight * ratio))
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  canvas.getContext('2d').drawImage(img, 0, 0, w, h)
  return canvas
}

// 仅在体积过大时降采样用（正常走原图直存）
export function imageToBlob(img, maxEdge, quality = 0.92) {
  return new Promise((resolve) => {
    drawToCanvas(img, maxEdge).toBlob((b) => resolve(b), 'image/jpeg', quality)
  })
}

// 首帧占位小图（已不再使用，保留以防历史数据迁移参考）
export function imageToDataUrl(img, maxEdge, quality = 0.6) {
  return drawToCanvas(img, maxEdge).toDataURL('image/jpeg', quality)
}
