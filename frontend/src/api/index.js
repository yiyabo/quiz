import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // 未授权，清除token并跳转登录
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 用户认证API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me')
}

// 竞赛API
export const competitionAPI = {
  getCompetitions: () => api.get('/competitions'),
  getCompetition: (id) => api.get(`/competitions/${id}`)
}

// 提交API
export const submissionAPI = {
  submit: (competitionId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/submissions?competition_id=${competitionId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getMySubmissions: (limit = 50) => api.get('/submissions/me', { params: { limit } }),
  getSubmission: (id) => api.get(`/submissions/${id}`)
}

// 排行榜API
export const leaderboardAPI = {
  getLeaderboard: (competitionId = null, limit = 100) => {
    const params = { limit }
    if (competitionId) params.competition_id = competitionId
    return api.get('/leaderboard', { params })
  }
}

// 统计API
export const statisticsAPI = {
  getStatistics: () => api.get('/statistics')
}

// 数据下载API
export const downloadAPI = {
  getDatasetUrl: (competitionId) => `/api/download/dataset/${competitionId}`
}

export default api

