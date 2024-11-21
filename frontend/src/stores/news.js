import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import axios from 'axios'

export const useNewsStore = defineStore('news', () => {
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()
  const userStore = useUserStore()
  const news = ref([])

  const crawlNews = function() {
    console.log("GOGOGOGOOGGOO")
    axios({
      method: 'get',
      url: `${API_URL}/crawl/`,
      headers: {
        Authorization: `Token ${userStore.token}`
      }
    }).then((response) => {
      console.log("Successfully crawled")
    })
  }

  return { news, crawlNews }
})
