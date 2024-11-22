<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNewsStore } from '@/stores/news'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

const userStore = useUserStore()

const newsStore = useNewsStore()

const title = ref(null)
const content = ref(null)

const crawlNews = function() {
  newsStore.crawlNews()
}

const listUpNews = function() {
    newsStore.listUpNews()
}

const getSummarization = function() {
    newsStore.getSummarization()
}

// const posts = newsStore.news;
const posts = computed(() => newsStore.news);

// 현재 페이지와 페이지당 항목 수
const currentPage = ref(1);
const pageSize = 10;

// 요약 데이터를 저장할 객체
const summaries = ref({});

// 현재 페이지에 해당하는 뉴스 계산
const paginatedPosts = computed(() => {
  if (!Array.isArray(posts.value)) {
    return []; // posts.value가 배열이 아닐 경우 빈 배열 반환
  }
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return posts.value.slice(start, end);
});

// 총 페이지 수 계산
const totalPages = computed(() => {
  if (!Array.isArray(posts.value)) {
    return []; // posts.value가 배열이 아닐 경우 빈 배열 반환
  }
  return Math.ceil(posts.value.length / pageSize);
});

// 페이지 이동 함수
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

// Summarize 버튼 동작
const summarize = (postId) => {
  // Django API 호출 후 요약 데이터 받아오기
//   getSummarization(postId)
    axios({
        method: 'get',
        url: `${API_URL}/crawl/news_summarize/${postId}`,
        headers: {
            Authorization: `Token ${userStore.token}`
        },
    }).then((response) => {
        console.log("Successfully summarized")
        console.log(response.data)

        summaries.value[postId] = `This is a summarized version of news:\n ${response.data.message}.`;
    })

    console.log(`Summarizing post ID: ${postId}`);
    // 테스트 요약 데이터 추가
    // summaries.value[postId] = `This is a summarized version of post ID ${postId}.`;
};

// 화면 뜨면 새로 갱신
onMounted(() => {
    listUpNews();
});

</script>

<template>
  <div>
    <h1>뉴스 보는 곳</h1>
    <form @submit.prevent="listUpNews">
      <input type="submit" value="뉴스 list하기">
    </form>
    <form @submit.prevent="crawlNews">
      <input type="submit" value="뉴스 갱신하기">
    </form>
  </div>
  <!-- <p v-for="(item, index) in posts" :key="index">{{ item }}</p> -->
  
  <h1>📰 뉴스 리스트</h1>

    <!-- 뉴스 리스트 -->
    <div v-for="(post, index) in paginatedPosts" :key="post.id" class="news-item">
      <hr /> <!-- 수평 라인 -->

      <!-- 제목 -->
      <h2>제목: {{ post.title }}</h2>

      <!-- 내용 -->
      <p class="content">내용: {{ post.content }}</p>

      <!-- 키워드 출력 -->
      <p class="keyword">키워드: {{ post.keywords }}</p>

      <!-- Summarize 버튼 -->
      <button 
        class="summarize-button" 
        @click="summarize(post.id)" 
      >
        Summarize
      </button>

      <!-- 요약 결과 표시 -->
      <div v-if="summaries[post.id]" class="summary-box">
        <strong>요약:</strong>
        <p>{{ summaries[post.id] }}</p>
      </div>
    </div>

    <!-- 페이지 이동 버튼 -->
    <div class="pagination">
      <button 
        class="nav-button" 
        :disabled="currentPage === 1" 
        @click="prevPage"
      >
        이전
      </button>
      <button 
        class="nav-button" 
        :disabled="currentPage === totalPages" 
        @click="nextPage"
      >
        다음
      </button>
    </div>

</template>

<style scoped>
/* 전체 컨테이너 */
.news-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  color: #333;
}

/* 제목 스타일링 */
h1 {
  text-align: center;
  color: #4CAF50;
  font-size: 2rem;
  margin-bottom: 20px;
}

/* 뉴스 아이템 */
.news-item {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f9f9f9;
}

/* 뉴스 제목 */
.news-item h2 {
  font-size: 1.5rem;
  color: #222;
  margin-bottom: 10px;
}

/* 뉴스 내용 */
.content {
  font-size: 1rem;
  color: #555;
  line-height: 1.5;
  margin-bottom: 10px;
}

/* 요약 상자 */
.summary-box {
  margin-top: 10px;
  padding: 10px;
  background-color: #e7f4e7;
  border-left: 5px solid #4CAF50;
  border-radius: 5px;
}

/* Summarize 버튼 */
.summarize-button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  text-align: center;
}

.summarize-button:hover {
  background-color: #45a049;
}

/* 페이지 네비게이션 */
.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.nav-button {
  padding: 10px 20px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.nav-button:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}

.nav-button:hover:enabled {
  background-color: #0056b3;
}
</style>