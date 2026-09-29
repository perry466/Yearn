import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(config => {
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.detail || '请求失败，请检查网络'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

export function useApi() {
  // 生日列表
  const listBirthdays = (params = {}) => api.get('/birthdays', { params })

  // 即将到来
  const listUpcoming = (days = 30) => api.get('/birthdays/upcoming', { params: { days } })

  // 统计
  const getStats = () => api.get('/birthdays/stats')

  // 日历
  const getCalendar = (year, month) => api.get('/birthdays/calendar', { params: { year, month } })

  // 详情
  const getBirthday = (id) => api.get(`/birthdays/${id}`)

  // 创建
  const createBirthday = (data) => api.post('/birthdays', data)

  // 更新
  const updateBirthday = (id, data) => api.put(`/birthdays/${id}`, data)

  // 删除
  const deleteBirthday = (id) => api.delete(`/birthdays/${id}`)

  // 系统设置
  const getSettings = () => api.get('/settings')
  const updateSettings = (data) => api.put('/settings', data)
  const testReminder = () => api.post('/settings/test')

  return {
    listBirthdays,
    listUpcoming,
    getStats,
    getCalendar,
    getBirthday,
    createBirthday,
    updateBirthday,
    deleteBirthday,
    getSettings,
    updateSettings,
    testReminder,
  }
}
