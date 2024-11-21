<script setup>
import { ref } from 'vue'
import { useBoardStore } from '@/stores/board'

const boardStore = useBoardStore()

const title = ref(null)
const content = ref(null)

const createBoard = function() {
  const payload = {
    title: title.value,
    content: content.value
  }
  boardStore.createBoard(payload)
}

</script>

<template>
  <div>
    <h1>게시글 생성</h1>
    <form @submit.prevent="createBoard">
      <div>
        <label for="title">title: </label>
        <input 
          type="text" 
          id="title"
          v-model="title" 
          placeholder="제목을 입력하세요"
          >
      </div>

      <div>
        <label for="content">content: </label>
        <textarea 
          v-model="content"
          placeholder="내용을 입력하세요"
          ></textarea>
      </div>

      <input type="submit" value="게시글 생성하기">
    </form>
  </div>
</template>

<style scoped>

</style>