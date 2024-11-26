<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password1 = ref('')
const password2 = ref('')

const signUp = async () => {
  if (password1.value !== password2.value) {
    alert('비밀번호가 일치하지 않습니다.')
    return
  }
  
  try {
    const payload = { username: username.value, password1: password1.value, password2: password2.value }
    await userStore.signUp(payload)
    router.push('/login')  // 회원가입 후 로그인 페이지로 리다이렉트
  } catch (error) {
    console.error('회원가입 실패:', error)
    alert('회원가입 실패')
  }
}
</script>

<template>
  <div class="container d-flex justify-content-center align-items-center custom-container">
    <div class="signup-box p-4 shadow-sm rounded">
      <h1 class="mb-4">회원가입</h1>
      <form @submit.prevent="signUp">
        <div class="mb-3">
          <label for="username" class="form-label">사용자 이름</label>
          <input 
            type="text" 
            id="username" 
            class="form-control" 
            v-model="username" 
            required
          />
        </div>
        <div class="mb-3">
          <label for="password1" class="form-label">비밀번호</label>
          <input 
            type="password" 
            id="password1" 
            class="form-control" 
            v-model="password1" 
            required
          />
          <small class="form-text text-muted">영문자, 숫자 혼합 10글자 이상</small>
        </div>
        <div class="mb-3">
          <label for="password2" class="form-label">비밀번호 확인</label>
          <input 
            type="password" 
            id="password2" 
            class="form-control" 
            v-model="password2" 
            required
          />
        </div>
        <button type="submit" class="btn btn-primary w-100">회원가입</button>
      </form>
      <div class="mt-3 text-center">
        <p>이미 계정이 있으신가요? <router-link to="/login">로그인</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.signup-box {
  width: 100%;
  max-width: 500px; /* 동일한 크기 설정 */
  height: 500px; /* 로그인 박스 크기에 맞춰 설정 */
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.custom-container {
  background-color: #ffffff;
  min-height: 70vh; /* 화면 상단에 더 가까운 위치 */
}

.container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* 위쪽 정렬 */
  min-height: 100vh;
}

.form-text {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 5px;
}
</style>
