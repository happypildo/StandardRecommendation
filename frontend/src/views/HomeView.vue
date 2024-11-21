<script setup>
import { useUserStore } from '@/stores/user'
import { useBoardStore } from '@/stores/board'
// setup: 아직 틀(DOM)이 완성되지 않음
// onMounted: 라이프 사이클 훅
//    데이터가 그려질 틀(DOM)이 완성되고 난 후 시점
// API 를 통해 데이터를 가져오는 시점
//  -> 틀이 완성되고 난 후
//  -> onMounted 안에 작성해주어야 한다.
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const userStore = useUserStore()
const boardStore = useBoardStore()

onMounted(() => {
  boardStore.getBoards()
})

const goCreateBoard = function() {
  router.push('/create-board')
}
</script>

<template>
  <div>
    <h1>게시글 출력</h1>
    <p v-if="userStore.loginUsername">로그인된 사용자: {{ userStore.loginUsername }}</p>
    <button 
      v-if="userStore.loginUsername"
      @click="goCreateBoard"
    >게시글 생성하기</button>
    <div 
      v-for="board in boardStore.boards"
      :key="board.id"
      >
      <p>{{ board.id }}번째 글</p>
      <p>제목: {{ board.title }}</p>
      <p>내용: {{ board.content }}</p>
      <p>작성자: {{ board.writer }}</p>
      <hr>
    </div>
  </div>
</template>

<style scoped>

</style>