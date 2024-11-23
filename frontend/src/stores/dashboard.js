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
    const sankeyData = ref([])
    const plotImg = ref([])

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

    const getSankeyData = function() {
        console.log('Trying to get sankey data...')
        axios({
            method: 'get',
            url: `${API_URL}/crawl/relationship/`,
            headers: {
                Authorization: `Token ${userStore.token}`
            }
        }).then((response)=>{
            console.log("Sankey Data: ")
            console.log(response.data)
            sankeyData.value = response.data
        })
    }

    const getPlotImg = function(release_num) {
        console.log(`Trying to get plot-image by ${release_num}`)
        axios({
            method: 'get',
            url: `${API_URL}/crawl/release_relation/${release_num}/`,
            headers: {
                Authorization: `Token ${userStore.token}`
            }
        }).then((response) => {
            console.log(response.data)
            console.log(response.data.image)
            // plotImg.value = response.data.image
            plotImg.value = `data:image/png;base64,${response.data.image}`;
        })
    }

    return { dashboards, wordClouds, sankeyData, plotImg, getWordCloudInfo, getPlotImg, getSankeyData}
})
