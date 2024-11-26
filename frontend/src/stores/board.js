import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import axios from 'axios'

export const useBoardStore = defineStore('board', () => {
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()
  const userStore = useUserStore()
  const boards = ref([])

  const getBoards = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/`)
      boards.value = response.data
    } catch (error) {
      console.error('게시글 목록 가져오기 실패:', error)
    }
  }

  const createBoard = async (payload) => {
    try {
      const { title, content } = payload
      const token = userStore.getToken // getter를 통해 토큰 가져오기
      if (!token) {
        throw new Error('유효한 토큰이 없습니다.')
      }

      await axios.post(
        `${API_URL}/api/v1/`,
        { title, content },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      )
      alert('게시글 생성 완료')
      router.push('/')
    } catch (error) {
      console.error('게시글 생성 실패:', error)
    }
  }

  return { boards, getBoards, createBoard }
})
