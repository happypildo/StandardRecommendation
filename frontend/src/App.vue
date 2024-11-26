<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const boards = ref([])

const router = useRouter()
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 게시글 목록을 가져오기
onMounted(() => {
  userStore.restoreSession()
  axios.get('http://localhost:8000/api/v1/')
    .then(response => {
      boards.value = response.data
    })
    .catch(error => console.error(error))
})
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm mb-4">
    <div class="container">
      <!-- 브랜드 로고 -->
      <RouterLink to="/" class="navbar-brand">SSAFY</RouterLink>

      <!-- 모바일 메뉴 토글 버튼 -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 네비게이션 메뉴 -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <RouterLink to="/" class="nav-link">커뮤니티</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/login" class="nav-link">로그인</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/logout" class="nav-link">로그아웃</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/signup" class="nav-link">회원가입</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/news" class="nav-link">뉴스</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/Dashboard" class="nav-link">대시보드</RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- RouterView 에 경로에 해당하는 컴포넌트가 출력된다. -->
  <RouterView />
</template>

<style scoped>
.navbar-brand {
  font-weight: bold;
  font-size: 1.25rem;
  color: #007bff !important;
}

.nav-link {
  font-size: 1rem;
  padding: 0.5rem 1rem;
}

.nav-link:hover {
  color: #0056b3 !important;
  text-decoration: underline;
}
</style>
