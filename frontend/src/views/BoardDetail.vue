<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const board = ref(null)
const commentContent = ref('')
const route = useRoute()
const isLoading = ref(false)
const error = ref(null)
const isCommentLoading = ref(false)
const commentError = ref(null)

onMounted(async () => {
  try {
    isLoading.value = true
    const baseURL = 'http://localhost:8000/api/boards'  // 실제 서버 주소로 변경
    console.log('게시글 ID:', route.params.id) // route.params.id 값 확인
    const response = await axios.get(`${baseURL}/${route.params.id}/`)
    console.log('API 응답:', JSON.stringify(response.data, null, 2))
    board.value = response.data
  } catch (err) {
    console.error('게시글을 불러오는 중 오류가 발생했습니다:', err)
    if (err.response) {
      error.value = `Error: ${err.response.status} - ${err.response.data.detail || '알 수 없는 오류'}`;
    } else {
      error.value = '게시글을 불러오는 중 네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
})

const addComment = async () => {
    console.log('Sending comment data:', { content: commentContent.value });
  if (!commentContent.value.trim()) {
    commentError.value = '댓글 내용을 입력해주세요.'
    return
  }

  try {
    isCommentLoading.value = true
    commentError.value = null
    const response = await axios.post(`http://localhost:8000/api/boards/${route.params.id}/comment/`, { content: commentContent.value })
    if (!board.value.comments) {
      board.value.comments = []
    }
    board.value.comments.push(response.data)
    commentContent.value = ''
  } catch (error) {
    console.error('댓글 작성 중 오류가 발생했습니다:', error)
    commentError.value = '댓글 작성에 실패했습니다. 다시 시도해주세요.'
  } finally {
    isCommentLoading.value = false
  }
}

const toggleFavorite = async () => {
  try {
    if (board.value.isFavorite) {
      await axios.delete(`/api/boards/${route.params.id}/favorite/`)
      board.value.isFavorite = false
    } else {
      await axios.post(`/api/boards/${route.params.id}/favorite/`)
      board.value.isFavorite = true
    }
  } catch (error) {
    console.error('즐겨찾기 처리 오류:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString() // 또는 원하는 형식으로 포맷팅
}
</script>

<template>
  <div class="container mt-5">
    <div v-if="isLoading">게시글을 불러오는 중입니다...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="board" class="card mb-3 shadow-sm">
      <div class="card-body">
        <h1 class="card-title">{{ board.title }}</h1>
        <p class="card-text">{{ board.content }}</p>
        <p v-if="board.writer" class="text-muted small">
          <strong>작성자:</strong> {{ board.writer }}
        </p>
        <p v-if="board.created_at" class="text-muted small">
          <strong>작성일:</strong> {{ formatDate(board.created_at) }}
        </p>

        <!-- <button 
          @click="toggleFavorite" 
          class="btn btn-outline-primary mt-3"
        >
          {{ board.isFavorite ? '즐겨찾기 삭제' : '즐겨찾기 추가' }}
        </button> -->
      </div>
    </div>

    <section v-if="board" class="mt-4">
      <h2>댓글</h2>

      <div v-for="comment in board.comments" :key="comment.id" class="card mb-2 shadow-sm">
        <div class="card-body">
          <p><strong>{{ comment.user }}:</strong> {{ comment.content }}</p>
        </div>
      </div>

      <div class="mt-3">
        <textarea 
            v-model="commentContent" 
            class="form-control" 
            rows="3" 
            placeholder="댓글을 입력하세요"
            :disabled="isCommentLoading"
        ></textarea>
        <p v-if="commentError" class="text-danger">{{ commentError }}</p>
        <button 
            @click="addComment" 
            class="btn btn-primary mt-2"
            :disabled="isCommentLoading"
        >
            {{ isCommentLoading ? '작성 중...' : '댓글 작성' }}
        </button>
        </div>
    </section>

    <div v-else-if="!isLoading && !error" class="alert alert-warning">
      게시글을 찾을 수 없습니다.
    </div>
  </div>
</template>
