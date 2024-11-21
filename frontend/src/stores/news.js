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
      url: `${API_URL}/crawl/renew/`,
      headers: {
        Authorization: `Token ${userStore.token}`
      }
    }).then((response) => {
      console.log("Successfully crawled")
    })
  }

  const listUpNews = function() {
    console.log("listUp btn is clicked...")
    axios({
        method: 'get',
        url: `${API_URL}/crawl/list/`,
        headers: {
          Authorization: `Token ${userStore.token}`
        }
      }).then((response) => {
        console.log("Successfully listed up")
        console.log(response.data)
        news.value = response.data
      })
  }

  const getSummarization = function(id) {
    console.log("Summarization is clicked...")
    console.log(id)
    axios({
        method: 'get',
        url: `${API_URL}/crawl/summarize/`,
        headers: {
            Authorization: `Token ${userStore.token}`
        },
        params: {
            id: id
        }
    }).then((response) => {
        console.log("Successfully summarized")
        console.log(response.data)
    })
  }

  return { news, crawlNews, listUpNews, getSummarization }
})
