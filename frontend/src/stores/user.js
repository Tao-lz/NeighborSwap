import { defineStore } from 'pinia'
import api from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.user,
    nickname: (s) => s.user?.nickname || '',
    userId: (s) => s.user?.id || null,
  },
  actions: {
    async login(nickname) {
      const { data } = await api.post('/users/login', { nickname })
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },
    logout() {
      this.user = null
      localStorage.removeItem('user')
    },
  },
})
