<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <nav>
    <!-- RouterLink 에서 경로를 선택하고 -->
    <RouterLink to="/">메인 페이지</RouterLink> |
    <RouterLink to="/login">로그인</RouterLink> |
    <RouterLink to="/signup">회원가입</RouterLink> |
    <RouterLink to="/news">news</RouterLink> 
  </nav>

  <!-- RouterView 에 경로에 해당하는 컴포넌트가 출력된다. -->
  <RouterView />
</template>

<style scoped>

</style>
