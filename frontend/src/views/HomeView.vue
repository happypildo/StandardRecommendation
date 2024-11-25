<script setup>
import { useUserStore } from '@/stores/user'
import { useBoardStore } from '@/stores/board'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()
const boardStore = useBoardStore()

// 게시판 데이터를 불러오는 로직
onMounted(async () => {
  try {
    await boardStore.getBoards()  // 비동기 호출 대기
    console.log('Boards:', boardStore.boards)  // 데이터 확인용
  } catch (error) {
    console.error('게시판 데이터를 불러오는 중 오류가 발생했습니다:', error)
  }
})

const goCreateBoard = () => {
  router.push('/create-board')
}

const goToBoardDetail = (id) => {
  router.push({ name: 'board-detail', params: { id } })  // 상세 페이지로 이동
}
</script>

<template>
  <div class="container mt-5">
    <header class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3">게시판</h1>
      <div v-if="userStore.loginUsername">
        <span class="text-muted me-3">환영합니다, {{ userStore.loginUsername }}님!</span>
        <button 
          class="btn btn-primary"
          @click="goCreateBoard"
        >
          + 글쓰기
        </button>
      </div>
    </header>

    <section>
      <!-- 데이터가 비어 있을 경우 메시지 표시 -->
      <div v-if="boardStore.boards.length === 0">
        <p>게시글이 없습니다.</p>
      </div>

      <!-- 게시글 목록 렌더링 -->
      <div 
        v-for="board in boardStore.boards" 
        :key="board.id" 
        class="card mb-3 shadow-sm"
        @click="goToBoardDetail(board.id)" 
        style="cursor: pointer;"
      >
        <div class="card-body">
          <h5 class="card-title">{{ board.title }}</h5>
          <p class="card-text text-truncate">{{ board.content }}</p>
          <div class="text-muted small">
            작성자: {{ board.writer }} | 글 번호: {{ board.id }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.card-text.text-truncate {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
