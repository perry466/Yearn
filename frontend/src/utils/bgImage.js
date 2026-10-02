// 背景图原图存储：localStorage 装不下高分辨率图，改用 IndexedDB（容量按磁盘算，几乎不限）
// 上传时若长边不超过 MAX_EDGE，直接存原始文件字节，不做任何二次编码，画质零损失。

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

export const putBgBlob = (mode, blob) => withStore((s) => s.put(blob, mode))
export const getBgBlob = (mode) => withStore((s) => s.get(mode))
export const delBgBlob = (mode) => withStore((s) => s.delete(mode))

// 把 File/Blob 解码成 HTMLImageElement
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

// 仅在体积过大时降采样用（正常情况下走原图直存）
export function imageToBlob(img, maxEdge, quality = 0.92) {
  return new Promise((resolve) => {
    drawToCanvas(img, maxEdge).toBlob((b) => resolve(b), 'image/jpeg', quality)
  })
}

// 首帧占位小图（几 KB，可安全放进 localStorage）
export function imageToDataUrl(img, maxEdge, quality = 0.6) {
  return drawToCanvas(img, maxEdge).toDataURL('image/jpeg', quality)
}
