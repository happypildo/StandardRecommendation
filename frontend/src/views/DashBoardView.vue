<script setup>
import WordCloud from "@/views/WordCloud.vue";
import { computed, onMounted } from "vue";
import { useDashBoardStore } from "@/stores/dashboard";

const dashboardStore = useDashBoardStore();

// wordCloud 데이터를 computed로 참조
const wcInfo = computed(() => dashboardStore.wordClouds);

// WordCloud 정보를 가져오는 함수
const getWordCloudInfo = () => {
    dashboardStore.getWordCloudInfo();
};

// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(() => {
    getWordCloudInfo();
    console.log("Updated wcInfo after getWordCloudInfo:", wcInfo.value);
});
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
</style>
