import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import axios from 'axios'

export const useBoardStore = defineStore('board', () => {
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()
  const userStore = useUserStore()
  const boards = ref([])

  const getBoards = function() {
    axios({
      method: 'get',
      url: `${API_URL}/api/v1/`
    }).then((response) => {
      console.log(response)
      boards.value = response.data
    }).catch((error) => {
      console.log(error)
    })
  }

  const createBoard = function(payload) {
    const { title, content } = payload

    axios({
      method: 'post',
      url:  `${API_URL}/api/v1/`,
      data: {
        title,
        content
      },
      headers: {
        Authorization: `Token ${userStore.token}`
      }
    }).then((response) => {
      alert("게시글 생성 완료")
      router.push('/')
    }).catch((error) => {
      console.log(error)
    })
  }

  return { boards, getBoards, createBoard }
})
