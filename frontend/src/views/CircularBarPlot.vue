<template>
  <div class="c-chart-container">
    <!-- 설명 1 -->
    <div class="c-chart-item">
      <h2>🙄 요즘 트렌드에 나는 얼마나 맞춰가고 있을까 (*/ω＼*)</h2>
      <p> ❤️❤️❤️ 색칠된 영역을 선택해 부족한 나의 사랑을 채우자! ❤️❤️❤️ </p>
      <div ref="circularPlot" class="circular-plot"></div>
    </div>

    <!-- 설명 2 -->
    <div class="c-chart-item">
      <h2>📰 통신에 사랑을 주기 위한 추천 뉴스</h2>
      <p v-show="selectedData.name"> {{ selectedData.name }} </p>
      <p v-show="!selectedData.name"> 키워드를 선택하세요! </p>
      <div ref="detailsContainer" class="details-container" v-show="selectedData">
        <div
          v-for="(news, index) in displayedNews"
          :key="index"
          class="news-box"
          @click="openModal(news)"
        >
          <h3>📰 추천 뉴스 - {{ news.title }}</h3>
          <p>📜 내용: {{ news.content.substring(0, 300) }}...</p>
        </div>
      </div>
    </div>

    <!-- 모달 -->
    <div v-if="isModalOpen" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ selectedNews.title }}</h2>
        <p>{{ selectedNews.content }}</p>
        <button class="close-button" @click="closeModal">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { useDashBoardStore } from "@/stores/dashboard";
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000';

const dashboardStore = useDashBoardStore();
const trendsData = computed(() => dashboardStore.trendsData || []);
const getNewsTrendsData = () => {
  dashboardStore.getNewsTrendsData();
};

const chart = ref(null);
const circularPlot = ref(null);
let selectedData = ref({});
const displayedNews = ref([{ title: "키워드를 선택해서", content: "추천 뉴스를 받아보세요." }]); // 표시할 뉴스 데이터

// 모달 관련 데이터
const isModalOpen = ref(false);
const selectedNews = ref({});

// 모달 열기
const openModal = (news) => {
  selectedNews.value = news;
  isModalOpen.value = true;
};

// 모달 닫기
const closeModal = () => {
  isModalOpen.value = false;
  selectedNews.value = {};
};


// Circular Barplot 렌더링 함수
const drawCircularBarplot = (data, offsetX = 0, id = "primary") => {
  const container = circularPlot.value.getBoundingClientRect();
  const width = container.width || 600;
  const height = container.height || 600;
  const innerRadius = 100;
  const outerRadius = Math.min(width, height) / 2 - 20;

  // 기존 SVG 제거
  d3.select(circularPlot.value).select(`#${id}`).remove();

  const svg = d3
    .select(circularPlot.value)
    .append("svg")
    .attr("id", id)
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2.6 + offsetX}, ${height / 2})`);

  // X 축 (각도를 위한 스케일)
  const x = d3
    .scaleBand()
    .range([0, 2 * Math.PI])
    .domain(data.map((d) => d.name));

  // Y 축 (반지름 스케일)
  const y = d3.scaleLinear().range([innerRadius, outerRadius]).domain([0, 1]);

  // 색상 스케일
  const color = d3.scaleOrdinal(d3.schemeCategory10).domain(data.map((d) => d.name));

  // Full value bar 추가 (투명도 처리)
  svg
    .append("g")
    .selectAll("path")
    .data(data)
    .join("path")
    .attr("fill", (d) => color(d.name))
    .attr("opacity", 0.2)
    .attr(
      "d",
      d3
        .arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius)
        .startAngle((d) => x(d.name))
        .endAngle((d) => x(d.name) + x.bandwidth())
        .padAngle(0.01)
        .padRadius(innerRadius)
    ).on("click", (event, d) => handleBarClick(d)); // 클릭 이벤트 추가

  // 실제 데이터 bar 추가
  svg
    .append("g")
    .selectAll("path")
    .data(data)
    .join("path")
    .attr("fill", (d) => color(d.name))
    .attr("d", d3.arc().innerRadius(innerRadius).outerRadius(innerRadius)) // 시작 위치 설정
    .on("mouseover", (event, d) => {
      // Hover 효과
      d3.select(event.target)
        .transition()
        .duration(200)
        .attr("fill", "orange");
    })
    .on("mouseout", (event, d) => {
      // Hover 효과 초기화
      d3.select(event.target)
        .transition()
        .duration(200)
        .attr("fill", color(d.name));
    })
    .transition() // 트랜지션 추가
    .duration(2000)
    .attrTween("d", function (d) {
    const interpolate = d3.interpolate(innerRadius, y(d.value)); // 0에서 value까지
    return function (t) {
      return d3
        .arc()
        .innerRadius(innerRadius)
        .outerRadius(interpolate(t)) // 현재 진행 상태 반영
        .startAngle(x(d.name))
        .endAngle(x(d.name) + x.bandwidth())
        .padAngle(0.01)
        .padRadius(innerRadius)();
    };
  });

  // 텍스트 추가
  svg
    .append("g")
    .selectAll("text")
    .data(data)
    .join("text")
    .attr("text-anchor", "middle")
    .attr("transform", (d) => {
      const angle = x(d.name) + x.bandwidth() / 2;
      const radius = y(d.value) + 40;
      const xPos = Math.sin(angle) * radius;
      const yPos = -Math.cos(angle) * radius;
      return `translate(${xPos}, ${yPos})`;
    })
    .text((d) => `${(d.value * 100).toFixed(1)}%`)
    .style("font-size", "20px")
    .style("fill", "#333")
    .style("opacity", 0)
    .transition() // 텍스트 트랜지션
    .duration(1000)
    .style("opacity", 1);

  // 범례 추가
  const legend = svg
    .append("g")
    .attr("transform", `translate(${outerRadius + 40}, ${-outerRadius})`);

  data.forEach((d, i) => {
    const legendItem = legend
      .append("g")
      .attr("transform", `translate(0, ${i * 50})`);

    legendItem
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", 15)
      .attr("height", 15)
      .attr("fill", color(d.name));

    legendItem
      .append("text")
      .attr("x", 20)
      .attr("y", 12)
      .text(d.name)
      .style("font-size", "18px")
      .style("fill", "#333");
  });
};


const handleBarClick = async (data) => {
  selectedData.value = data;

  try {
    const response = await axios.post(`${API_URL}/crawl/rec_news/`, {
      name: data.name,
    });

    if (response.status === 200 && response.data) {
      displayedNews.value = response.data.map((item) => ({
        title: `${item.title}`,
        content: `${item.content}`,
      }));
    } else {
      console.error("서버에서 데이터를 받지 못했습니다.");
      displayedNews.value = [
        { content: `${data.name} 관련 뉴스 1` },
        { content: `${data.name} 관련 뉴스 2` },
        { content: `${data.name} 관련 뉴스 3` },
      ];
    }
  } catch (error) {
    console.error("서버 요청 중 오류 발생:", error);
    displayedNews.value = [
      { content: `${data.name} 관련 뉴스 1 (오류 발생)` },
      { content: `${data.name} 관련 뉴스 2 (오류 발생)` },
      { content: `${data.name} 관련 뉴스 3 (오류 발생)` },
    ];
  }
};

onMounted(() => {
  getNewsTrendsData();
  if (trendsData.value.length) {
    drawCircularBarplot(trendsData.value, 0, "primary");
  }
});

watch(trendsData, (newData) => {
  if (newData.length) {
    drawCircularBarplot(newData, 0, "primary");
  }
});
</script>

<style scoped>
.c-chart-container {
  display: grid; /* 2x2 구조를 만들기 위해 grid 사용 */
  grid-template-columns: 7fr 3fr; /* 두 열로 나눔 */
  gap: 20px; /* 아이템 간 간격 */
  width: 100%;
  height: 100%;
  padding: 20px;
  background-color: #f9f9f9; /* 배경색 추가 */
  border-radius: 10px;
}

.c-chart-item h2 {
  height: 50px; /* 고정된 높이 설정 */
  line-height: 50px; /* 텍스트 수직 중앙 정렬 */
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.c-chart-item {
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
.circular-plot {
  width: 100%;
  height: 600px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.details-container {
  width: 100%;
  max-height: 600px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.news-box {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: left;
  border: 1px solid #ddd;
  cursor: pointer;
  transition: background-color 0.3s;
}

.news-box h3 {
  font-size: 20px;
}

.news-box:hover {
  background-color: #eaeaea;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7); /* 어둡게 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-in-out; /* 페이드 애니메이션 */
}

.modal-content {
  background: #ffffff;
  padding: 30px;
  border-radius: 15px;
  max-width: 800px;
  width: 90%;
  text-align: center;
  position: relative;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
  transform: scale(0.9);
  animation: scaleUp 0.3s ease-in-out forwards; /* 팝업 효과 */
}

.modal-content h2 {
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.modal-content p {
  font-size: 16px;
  color: #333;
  line-height: 1.8;
  text-align: justify; /* 텍스트 정렬 */
  max-height: 60vh; /* 스크롤 제한 */
  overflow-y: auto;
  padding: 20px; /* 내부 여백 추가 */
  background-color: #f9f9f9; /* 박스 배경색 */
  border-radius: 10px; /* 둥근 모서리 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* 박스 그림자 */
  margin-bottom: 15px; /* 여러 문단 간 간격 */
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: transparent;
  border: none;
  font-size: 20px;
  font-weight: bold;
  color: #999;
  cursor: pointer;
  transition: color 0.3s;
}

.close-button:hover {
  color: #333;
}

.close-button:focus {
  outline: none;
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    background-color: rgba(0, 0, 0, 0);
  }
  to {
    background-color: rgba(0, 0, 0, 0.7);
  }
}

@keyframes scaleUp {
  from {
    transform: scale(0.9);
  }
  to {
    transform: scale(1);
  }
}
</style>