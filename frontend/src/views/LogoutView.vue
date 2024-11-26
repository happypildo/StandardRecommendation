<script setup>
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const logOut = async () => {
  try {
    await userStore.logOut()
    router.push('/login')  // 로그아웃 후 로그인 페이지로 리다이렉트
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

logOut()  // 페이지가 로드될 때 로그아웃 처리
</script>

<template>
  <div class="container mt-5">
    <h1>로그아웃 중...</h1>
    <p>잠시만 기다려주세요...</p>
  </div>
</template>

<style scoped>
</style>
