<script setup>
import WordCloud from "@/views/WordCloud.vue";
import ChordDiagram from "./ChordDiagram.vue";
import SankeyDiagram from "./Sankey.vue";
import NetworkGraph from "./NetworkGraph.vue";
import BarGraph from "./BarGraph.vue";
import Circular from "./CircularBarPlot.vue";
import SecondRow from "./SecondRow.vue";


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

// Sankey
const getSankeyData = () => {
  dashboardStore.getSankeyData();
}

// 챗봇
// 챗봇과 사용자의 모든 메시지를 관리하는 반응형 배열
const messages = ref([
  { sender: "bot", text: "안녕하세요! 저는 챗봇입니다. 무엇을 도와드릴까요?" },
  { sender: "bot", text: "📚 저는 입력해주신 내용을 바탕으로 3개의 표준 문서를 추천해 드릴 수 있어요! 당신의 통신을 향한 사랑을 제가 적합한 표준 문서로 보답해 드릴게요❤️❤️❤️" },
  { sender: "bot", text: "🔠 입력 예시) Study on mmWave" },
]); // 초기 챗봇 메시지
const currentMessage = ref(""); // 입력창에 입력된 메시지

const barData = ref([
  { label: "Category A", value: 30 },
  { label: "Category B", value: 50 },
  { label: "Category C", value: 70 },
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
        const botReponse = response.data.data;

        messages.value.push({sender:'bot', text: botReponse})
    }).catch((error) => {
        console.log(error)
        messages.value.push({sender:'bot', text: "서버와 연결할 수 없습니다."})
    })

    currentMessage.value = ""; // 입력창 초기화
};


// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(() => {
    getWordCloudInfo();
    getNetworkData(38);
    getSankeyData();

    barData.value = [
      { label: "Category A", value: 30 },
      { label: "Category B", value: 50 },
      { label: "Category C", value: 70 },
    ]
});

</script>

<template>
  <!-- <p> {{wcInfo}} </p>  -->

  <div class="dashboard">
      <header class="dashboard-header">
      <h2> 📊 Dashboard to check my deep love❤️ for WIRELESS COMMUNICATIONS  </h2>
      </header>
      <main class="dashboard-content">
          <h2> 💌 통신에 대한 나의 사랑은 얼마일까 (❁´◡`❁) </h2>
          <div class="row">
            <Circular/>
          </div>

          <h2> 💌 나에게 맞는 사랑🥰==통신🛜 표준은 무엇일까? (❁´◡`❁) </h2>
          <div class="row">
            <SecondRow />
          </div>
          
          <h2> 💌 나만의 키워드와 선택한 통신 표준 시리즈와의 ❤️관❤️계❤️ </h2>
          <div class="row">
            <NetworkGraph/>
          </div>
          
          <h2> 💌 챗봇🤖과의 대화를 통해 표준을 추천받아봐요! </h2>
          <div class="row">
            <div class="main-chart-container">
              <div class="main-chart-item">
                <h2> 🤖 챗봇과 자유롭게 얘기해 보아요 🤖 </h2>
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
              </div>
            </div>

            <div class="main-chart-container">
              <div class="main-chart-item">
                <h2> 내 입력과 추천된 문서들과의 유사도 </h2>
                <BarGraph :barData="barData"/>
              </div>
            </div>
          </div>
      </main>
      <footer class="dashboard-footer">
          <p>© 2024 My Dashboard</p>
      </footer>
  </div>
</template>

<style scoped>

.main-chart-container {
  display: flex; /* Flexbox로 변경 */
  justify-content: space-between; /* 요소 간 간격 균등 분배 */
  align-items: stretch; /* 모든 요소가 동일한 높이를 가짐 */
  gap: 20px;
  width: 100%;
  height: 100%; /* 부모 컨테이너 높이에 맞춤 */
}

.main-chart-item {
  flex: 1; /* 모든 요소가 동일한 비율로 공간을 차지 */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  height: 100%; /* 부모 Flex 컨테이너의 높이에 맞춤 */
}

.main-chart-item:first-child {
  margin-right: 10px; /* 첫 번째 아이템과 두 번째 아이템 사이의 간격 */
}

.main-chart-item:last-child {
  margin-left: 10px; /* 마지막 아이템과 첫 번째 아이템 사이의 간격 */
}

.main-chart-item h2 {
  height: 50px; /* 고정된 높이 설정 */
  line-height: 50px; /* 텍스트 수직 중앙 정렬 */
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}


.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 30px; /* 섹션 간의 간격을 넓힘 */
  padding: 20px;
  background-color: #f9f9f9; /* 전체 배경색 */
}

.dashboard-content h2 {
  font-size: 25px;
}

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