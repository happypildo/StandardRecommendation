<script setup>
import WordCloud from "@/views/WordCloud.vue";
import ChordDiagram from "./ChordDiagram.vue";
import SankeyDiagram from "./Sankey.vue";
import NetworkGraph from "./NetworkGraph.vue";
import BarGraph from "./BarGraph.vue";
import Circular from "./CircularBarPlot.vue";

import { ref, computed, onMounted, watch } from "vue";
import { useDashBoardStore } from "@/stores/dashboard";
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const dashboardStore = useDashBoardStore();
const userStore = useUserStore()
const API_URL = 'http://127.0.0.1:8000'

// wordCloud 데이터를 computed로 참조
const wcInfo = computed(() => dashboardStore.wordClouds);

// WordCloud 정보를 가져오는 함수
const getWordCloudInfo = () => {
    dashboardStore.getWordCloudInfo();
};

const serieses = Array.from({ length: 49 }, (_, i) => `${i}`)
const networkData = computed(() => dashboardStore.networkData)
const getNetworkData = (series_num) => {
    dashboardStore.getNetworkData(series_num);
}


// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(() => {
    getWordCloudInfo();
    getNetworkData(38);
    getSankeyData();
});

// Sankey
const getSankeyData = () => {
  dashboardStore.getSankeyData();
}

// 챗봇
// 챗봇과 사용자의 모든 메시지를 관리하는 반응형 배열
const messages = ref([
  { sender: "bot", text: "안녕하세요! 저는 챗봇입니다. 무엇을 도와드릴까요?" },
]); // 초기 챗봇 메시지
const currentMessage = ref(""); // 입력창에 입력된 메시지

const barData = ref([
  { label: "Category A", value: 30 },
  { label: "Category B", value: 50 },
]);

// Django에서 챗봇 응답을 받아오는 함수
const sendMessage = async () => {
    if (!currentMessage.value.trim()) return; // 빈 입력 방지

    // 사용자 메시지를 추가
    messages.value.push({ sender: "user", text: currentMessage.value });
    console.log(currentMessage.value)
    axios({
        method: 'post',
        url: `${API_URL}/crawl/chatbot/`,
        headers: {
            Authorization: `Token ${userStore.token}`,
            "Content-Type": "application/json",
        },
        data: {
            message: currentMessage.value
        },
    }).then((response) => {
        console.log(response.data)
        console.log(response.data.bar)
        console.log("Before Updated barData:", barData.value);
        barData.value = response.data.bar;
        // barData.value = [{'label': 'bb', 'value': 100}]
        console.log("After Updated barData:", barData.value);
        const botReponse = response.data

        messages.value.push({sender:'bot', text: botReponse})
    }).catch((error) => {
        console.log(error)
        messages.value.push({sender:'bot', text: "서버와 연결할 수 없습니다."})
    })

    currentMessage.value = ""; // 입력창 초기화
};

</script>

<template>
  <!-- <p> {{wcInfo}} </p>  -->

  <div class="dashboard">
      <header class="dashboard-header">
      <h1>Dashboard</h1>
      </header>
      <main class="dashboard-content">
          <h2> 💌 통신에 대한 나의 사랑은 얼마일까 (❁´◡`❁) </h2>
          <div class="row">
            <Circular/>
          </div>

          <!-- 첫 번째 행 -->
          <div class='chart-container'>
            <div class="chart-item">
                <h2> 📚 내가 관심있게 볼만한 표준 시리즈는 무엇일까 😲 </h2>
                <SankeyDiagram />
            </div>
            <div class='chart-item'>
              <h2> 💨 내가 관심있게 보았던 키워드들은 무엇이 있을까 🤔 </h2>
              <WordCloud :words="wcInfo" />
            </div>
          </div>

          <!-- 두 번째 행 -->
          <div class="row">
              <section class="spider-content">
                  <h2>Network graph</h2>
                  <NetworkGraph/>
              </section>

              <section class="chatbot-content">
                  <h2>Chatbot</h2>
                  <div class="barChart">
                    <h1>Bar graph</h1>
                    <BarGraph :barData="barData"/>
                  </div>

                  <div class="chat-container">
                      <!-- 채팅 메시지 영역 -->
                      <div class="chat-messages">
                          <!-- 메시지 목록 렌더링 -->
                          <div
                          class="chat-message"
                          :class="message.sender"
                          v-for="(message, index) in messages"
                          :key="index"
                          >
                          <p>{{ message.text }}</p>
                          </div>
                      </div>

                      <!-- 입력창 -->
                      <div class="chat-input">
                          <input
                          type="text"
                          v-model="currentMessage"
                          placeholder="챗봇에게 메시지 입력..."
                          @keyup.enter="sendMessage"
                          />
                          <button @click="sendMessage(currentMessage.value)">보내기</button>
                      </div>
                  </div>
              </section>
          </div>
      </main>
      <footer class="dashboard-footer">
          <p>© 2024 My Dashboard</p>
      </footer>
  </div>
</template>

<style scoped>
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 30px; /* 섹션 간의 간격을 넓힘 */
  padding: 20px;
  background-color: #f9f9f9; /* 전체 배경색 */
}

/* ---------------------------------------------------------------  */
.chart-container {
  display: grid; /* 2x2 구조를 만들기 위해 grid 사용 */
  grid-template-columns: 1fr 1fr; /* 두 열로 나눔 */
  gap: 20px; /* 아이템 간 간격 */
  width: 100%;
  height: 100%;
  padding: 20px;
  background-color: #f9f9f9; /* 배경색 추가 */
  border-radius: 10px;
}
.chart-item {
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 위쪽에 정렬 */
  align-items: center;
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}
.chart-item h2 {
  height: 50px; /* 고정된 높이 설정 */
  line-height: 50px; /* 텍스트 수직 중앙 정렬 */
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}
/* ---------------------------------------------------------------  */

.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 20px;
}

section {
  flex: 1;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

section:hover {
  transform: translateY(-3px); /* 박스를 약간 위로 올리는 효과 */
}

.word-cloud-section,
.sankey-section,
.spider-content,
.chatbot-content {
  max-width: 48%;
}

/* 제목 스타일 */
section h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
}

/* 챗봇 스타일 */
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chat-messages {
  flex: 1;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f9f9f9;
}

.chat-message.user {
  align-self: flex-end;
  background-color: #e8f0fe;
  color: #000;
  padding: 12px 18px;
  border-radius: 12px 12px 0 12px;
  font-size: 14px;
  max-width: 75%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-message.bot {
  align-self: flex-start;
  background-color: #fff;
  color: #000;
  padding: 12px 18px;
  border-radius: 12px 12px 12px 0;
  font-size: 14px;
  max-width: 75%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 15px;
  background-color: #fff;
  border-top: 1px solid #ddd;
}

.chat-input input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-input button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.chat-input button:hover {
  background-color: #0056b3;
}

/* 글쓰기 버튼 스타일 */
.dashboard-header button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dashboard-header button:hover {
  background-color: #0056b3;
}

</style>