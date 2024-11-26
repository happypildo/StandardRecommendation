<script setup>
import { ref } from 'vue'
import { useBoardStore } from '@/stores/board'

const boardStore = useBoardStore()

const title = ref('')
const content = ref('')

const createBoard = () => {
  const payload = {
    title: title.value,
    content: content.value,
  }
  boardStore.createBoard(payload)
}
</script>

<template>
  <div class="container mt-5">
    <header class="text-center mb-4">
      <h1 class="h3">새 글 작성</h1>
    </header>

    <form @submit.prevent="createBoard" class="card p-4 shadow-sm">
      <div class="mb-3">
        <label for="title" class="form-label">제목</label>
        <input 
          id="title" 
          type="text" 
          v-model="title" 
          placeholder="제목을 입력하세요" 
          class="form-control"
        />
      </div>

      <div class="mb-3">
        <label for="content" class="form-label">내용</label>
        <textarea 
          id="content" 
          v-model="content" 
          placeholder="내용을 입력하세요" 
          rows="6" 
          class="form-control"
        ></textarea>
      </div>

      <button 
        type="submit" 
        class="btn btn-primary w-100"
      >
        글 작성하기
      </button>
    </form>
  </div>
</template>

<style scoped>
</style>
