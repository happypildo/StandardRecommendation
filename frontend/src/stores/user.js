import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
    token: localStorage.getItem('access_token') || null, // 토큰 초기화
  }),
  getters: {
    getToken(state) {
      return state.token
    },
  },
  actions: {
    async logIn(payload) {
      try {
        const response = await axios.post('http://localhost:8000/dj-rest-auth/login/', {
          username: payload.username,
          password: payload.password,
        })
        console.log('로그인 응답 데이터:', response.data) // 응답 데이터 확인

        // const token = response.data.access
        const token = response.data.key
        // console.log(token)
        localStorage.setItem('access_token', token)
        axios.defaults.headers.common['Authorization'] = `Token ${token}` // axios 기본 헤더 설정
        this.isLoggedIn = true
        this.token = token
        this.user = payload.username
      } catch (error) {
        console.error('로그인 실패:', error)
        throw new Error('로그인 실패')
      }
    },

    async logOut() {
      localStorage.removeItem('access_token')
      delete axios.defaults.headers.common['Authorization']
      this.isLoggedIn = false
      this.token = null
      this.user = null
    },

    async signUp(payload) {
      try {
        const response = await axios.post('http://localhost:8000/dj-rest-auth/registration/', payload)
        const token = response.data.access
        localStorage.setItem('access_token', token)
        axios.defaults.headers.common['Authorization'] = `Token ${token}`
        this.isLoggedIn = true
        this.token = token
        this.user = payload.username
      } catch (error) {
        console.error('회원가입 실패:', error)
        throw new Error('회원가입 실패')
      }
    },

    async restoreSession() {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          axios.defaults.headers.common['Authorization'] = `Token ${token}`
          const response = await axios.get('http://localhost:8000/api/user/')
          this.isLoggedIn = true
          this.token = token
          this.user = response.data.username
        } catch (error) {
          console.error('세션 복구 실패:', error)
          this.logOut()
        }
      }
    },
  },
  persist: {
    enabled: true, // 상태 유지 활성화
  },
})
