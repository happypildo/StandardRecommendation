<script setup>
import WordCloud from "@/views/WordCloud.vue";
import ChordDiagram from "./ChordDiagram.vue";
import SankeyDiagram from "./Sankey.vue";
import NetworkGraph from "./NetworkGraph.vue";
import BarGraph from "./BarGraph.vue";
import Heatmap from "./Heatmap.vue";

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
          <div class="row">
            <h2> Heat map </h2>
            <Heatmap/>
          </div>

          <!-- 첫 번째 행 -->
          <div class="row">
              <section class="word-cloud-section">
                  <h2>Word Cloud</h2>
                  <!-- WordCloud 컴포넌트에 wcInfo 전달 -->
                  <WordCloud :words="wcInfo" />
              </section>
              
              <section class="sankey-section">
                  <h2>Sankey Diagram</h2>
                  <SankeyDiagram />
              </section>
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
  flex-direction: column; /* 기본 세로 정렬 */
  gap: 20px; /* 섹션 간 간격 */
}

.row {
  display: flex;
  flex-direction: row; /* 가로 정렬 */
  flex-wrap: nowrap; /* 가로로 한 줄에 배치 */
  justify-content: space-between; /* 양쪽 정렬 */
  gap: 20px; /* 섹션 간 간격 */
}

/* 각 섹션 크기 조정 */
section {
  flex: 1; /* 모든 섹션이 동일한 너비로 설정 */
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  min-width: 300px; /* 최소 너비 */
}

.word-cloud-section,
.sankey-section {
  max-width: 45%; /* 첫 번째 행에서 두 섹션이 각각 화면의 45% 차지 */
}

.spider-content,
.chatbot-content {
  max-width: 45%; /* 두 번째 행에서 두 섹션이 각각 화면의 45% 차지 */
}

.chatbot-content {
  margin-top: 20px;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.chat-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-messages {
  flex: 1;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.chat-message.user {
  align-self: flex-end;
  background-color: #e1f5fe;
  color: #000;
  padding: 10px 15px;
  border-radius: 10px 10px 0 10px;
  max-width: 70%;
  word-break: break-word;
  font-size: 14px;
}

.chat-message.bot {
  align-self: flex-start;
  background-color: #fff;
  color: #000;
  padding: 10px 15px;
  border-radius: 10px 10px 10px 0;
  max-width: 70%;
  word-break: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 14px;
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #ddd;
  background-color: #fff;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
}

.chat-input button {
  padding: 10px 15px;
  background-color: #6200ea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.chat-input button:hover {
  background-color: #3700b3;
}
</style>