import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
  }),
  actions: {
    async logIn(payload) {
      try {
        const response = await axios.post('http://localhost:8000/dj-rest-auth/login/', {
          username: payload.username,
          password: payload.password,  // 비밀번호는 payload에 추가
        })
        localStorage.setItem('access_token', response.data.access)
        this.isLoggedIn = true
        this.user = payload.username
      } catch (error) {
        throw new Error('로그인 실패')
      }
    },

    async logOut() {
      localStorage.removeItem('access_token')
      this.isLoggedIn = false
      this.user = null
    },

    async signUp(payload) {
      try {
        const response = await axios.post('http://localhost:8000/dj-rest-auth/registration/', payload)
        localStorage.setItem('access_token', response.data.access)
        this.isLoggedIn = true
        this.user = payload.username
      } catch (error) {
        throw new Error('회원가입 실패')
      }
    },
    async restoreSession() {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await axios.get('http://localhost:8000/api/user/', {
            headers: { Authorization: `Bearer ${token}` },
          })
          this.isLoggedIn = true
          this.user = response.data.username
        } catch (error) {
          console.error('세션 복구 실패:', error)
        }
      }
    },
  },
})