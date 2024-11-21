<script setup>
import { ref } from 'vue'
import { useNewsStore } from '@/stores/news'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const newsStore = useNewsStore()

const title = ref(null)
const content = ref(null)

const crawlNews = function() {
  newsStore.crawlNews()
}

</script>

<template>
  <div>
    <h1>뉴스 보는 곳</h1>
    <form @submit.prevent="crawlNews">
      <input type="submit" value="게시글 생성하기">
    </form>
  </div>
</template>

<style scoped>

</style>