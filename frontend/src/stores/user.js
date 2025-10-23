import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null,
    isLoggedIn: false
  }),

  actions: {
    // 初始化用户信息（从localStorage恢复）
    init() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.isLoggedIn = true
      }
    },

    // 登录
    async login(credentials) {
      const response = await authAPI.login(credentials)
      this.setAuth(response)
      return response
    },

    // 注册
    async register(userData) {
      const response = await authAPI.register(userData)
      this.setAuth(response)
      return response
    },

    // 设置认证信息
    setAuth(data) {
      this.token = data.access_token
      this.user = data.user
      this.isLoggedIn = true
      
      // 保存到localStorage
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
    },

    // 登出
    logout() {
      this.token = null
      this.user = null
      this.isLoggedIn = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})

