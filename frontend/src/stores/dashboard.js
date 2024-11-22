import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import axios from 'axios'


export const useDashBoardStore = defineStore('dashboard', () => {
    const API_URL = 'http://127.0.0.1:8000'
    const router = useRouter()
    const userStore = useUserStore()
    const dashboards = ref([])

    const wordClouds = ref([])

    const getWordCloudInfo = function() {
        console.log("Trying to get word-cloud information...")
        axios({
            method: 'get',
            url: `${API_URL}/crawl/wcinfo/`,
            headers: {
              Authorization: `Token ${userStore.token}`
            }
        }).then((response) => {
            console.log(response.data)
            console.log("Successfully get information!")

            // 데이터 가공: 키워드별로 그룹화 및 가중합
            const aggregatedData = response.data.reduce((acc, item) => {
                if (!acc[item.keyword]) {
                    // 키워드가 처음 등장하면 초기화
                    acc[item.keyword] = {
                        text: item.keyword, // `keyword`를 `text`로 매핑
                        size: 0 // `intensity` 합계 초기화
                    };
                }
                // 가중합 계산
                acc[item.keyword].size += item.intensity * 100;
                return acc;
            }, {});

            // wordClouds에 저장
            wordClouds.value = Object.values(aggregatedData);

            console.log(wordClouds.value)
        })
    }
    return { dashboards, wordClouds, getWordCloudInfo}
})
