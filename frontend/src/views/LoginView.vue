<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')

const logIn = async () => {
  try {
    const payload = { username: username.value, password: password.value }
    await userStore.logIn(payload)
    router.push('/')  // 로그인 후 홈 페이지로 리다이렉트
  } catch (error) {
    console.error('로그인 실패:', error)
    alert('로그인 실패')
  }
}
</script>

<template>
  <div class="container d-flex justify-content-center align-items-center custom-container">
    <div class="login-box p-4 shadow-sm rounded">
      <h1 class="mb-4">로그인</h1>
      <form @submit.prevent="logIn">
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
          <label for="password" class="form-label">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            class="form-control" 
            v-model="password" 
            required
          />
        </div>
        <button type="submit" class="btn btn-primary w-100">로그인</button>
      </form>
      <div class="mt-3 text-center">
        <p>아직 회원이 아니신가요? <router-link to="/signup">회원가입</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-box {
  width: 100%;
  max-width: 500px; /* 회원가입 박스와 동일한 크기 */
  height: 500px; /* 회원가입 박스 크기에 맞춰 설정 */
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
</style>
