<script setup>
import WordCloud from "@/views/WordCloud.vue";
import { ref, computed, onMounted } from "vue";
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

const releases = Array.from({ length: 17 }, (_, i) => `${i + 4}`)
const plotImg = computed(() => dashboardStore.plotImg)
const getPlotImg = (release_num) => {
    dashboardStore.getPlotImg(release_num);
}

// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(() => {
    getWordCloudInfo();
    console.log("Updated wcInfo after getWordCloudInfo:", wcInfo.value);
    getPlotImg(18);
    console.log("getPlotIMAGE")
});

// 챗봇
// 챗봇과 사용자의 모든 메시지를 관리하는 반응형 배열
const messages = ref([
  { sender: "bot", text: "안녕하세요! 저는 챗봇입니다. 무엇을 도와드릴까요?" },
]); // 초기 챗봇 메시지
const currentMessage = ref(""); // 입력창에 입력된 메시지

// Django에서 챗봇 응답을 받아오는 함수
const sendMessage = async () => {
    if (!currentMessage.value.trim()) return; // 빈 입력 방지

    // 사용자 메시지를 추가
    messages.value.push({ sender: "user", text: currentMessage.value });
    console.log(currentMessage.value)
    axios({
        method: 'get',
        url: `${API_URL}/crawl/chatbot/`,
        headers: {
            Authorization: `Token ${userStore.token}`,
            "Content-Type": "application/json",
        },
        data: {
            message: currentMessage.value,
        },
    }).then((response) => {
        console.log(response.data)

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
    <p> {{wcInfo}} </p> 

    <div class="dashboard">
        <header class="dashboard-header">
        <h1>Dashboard</h1>
        </header>
        <main class="dashboard-content">
            <section class="word-cloud-section">
                <h2>Word Cloud</h2>
                <!-- WordCloud 컴포넌트에 wcInfo 전달 -->
                <WordCloud :words="wcInfo" />
            </section>

            <section class="spider-content">
                <!-- 이미지 표시 영역 -->
                <div class="image-container">
                    <img :src="plotImg" alt="Generated Plot" v-if="plotImg" />
                    <p v-else>이미지를 로드하려면 번호를 선택하세요</p>
                </div>

                <!-- 버튼 리스트 -->
                <div class="button-list">
                    <button 
                    v-for="release in releases" 
                    :key="release" 
                    @click="getPlotImg(release)"
                    class="release-button"
                    >
                    Release {{ release }}
                    </button>
                </div>
            </section>

            <section class="chatbot-content">
                <h2>Chatbot</h2>
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
                    <button @click="sendMessage">보내기</button>
                </div>
                </div>
            </section>

        </main>
        <footer class="dashboard-footer">
            <p>© 2024 My Dashboard</p>
        </footer>
    </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
}

.dashboard-header {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}

.dashboard-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  flex-direction: column;
  gap: 20px;
}

.word-cloud-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.spider-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.container {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-top: 20px;
}

.image-container {
  width: 100%; /* 이미지 영역의 너비 */
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #ccc;
  padding: 10px;
  height: 1000px; /* 이미지 영역의 고정 높이 */
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.button-list {
  display: flex;
  flex-direction: column; /* 버튼을 수직으로 정렬 */
  margin-left: 20px;
}

.release-button {
  padding: 10px 20px;
  margin-bottom: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.release-button:hover {
  background-color: #0056b3;
}

.release-button:active {
  background-color: #003d80;
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
