import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
// useRouter: 특정 경로로 보낼 때
// useRoute: 받을 때
import { useRouter, useRoute } from 'vue-router'

export const useUserStore = defineStore('user', () => {
  // 나중에 배포할때는 API_URL 도 환경 변수로 빼줘야한다.
  // 내 PC 내부에서만 쓸 예정이니 하드코딩
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()
  const token = ref(null)
  const loginUsername = ref(null)

  const logIn = function (payload) {
    const { username, password } = payload

    axios({
      method: 'post',
      url: `${API_URL}/dj-rest-auth/login/`,
      data: {
        username,
        password
      }
    })
    // 성공 시 then, 실패 시 catch
    .then((response) => {
      console.log("response = ", response)
      token.value = response.data.key
      loginUsername.value = username
      
      router.push('/')
    })
    .catch((error) => {
      console.log("error = ", error)
    })
  }

  const signUp = function (payload) {
    const { username, password1, password2 } = payload

    axios({
      method: 'post',
      url: `${API_URL}/dj-rest-auth/registration/`,
      data: {
        username,
        password1,
        password2
      }
    }).then((response) => {
      alert('회원가입 성공!')
      logIn({ username, password: password1 })
    })
    .catch((error) => {
      console.log(error)
    })
  }

  const logOut = function () {
    axios({
      method: 'post',
      url: `${API_URL}/dj-rest-auth/logout/`,
      headers: {
        Authorization: `Token ${token}`
      }
    }).then((response) => {
      console.log('로그 아웃 완료!')
      alert('로그 아웃 완료!')
      // token = ref(null)
    })
    .catch((error) => {
      console.log(error)
    })
  }

  return { token, loginUsername, logIn, signUp, logOut }
}, { persist: true })