<template>
  <div class="chart-container">
    <!-- 설명 1 -->
    <div class="chart-item">
      <h2>🙄 요즘 트렌드에 나는 얼마나 맞춰가고 있을까 (*/ω＼*)</h2>
      <div ref="circularPlot" class="circular-plot"></div>
    </div>

    <!-- 설명 2 -->
    <div class="chart-item">
      <h2>📰 통신에 사랑을 주기 위한 추천 뉴스</h2>
      <div ref="detailsContainer" class="details-container" v-show="selectedData">
        <div v-for="(news, index) in displayedNews" :key="index" class="news-box">
          <h3>📰 추천 뉴스 - {{ news.title }}</h3>
          <p>📜 내용: {{ news.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { useDashBoardStore } from "@/stores/dashboard";
import axios from 'axios'
const API_URL = 'http://127.0.0.1:8000'

const dashboardStore = useDashBoardStore();
const trendsData = computed(() => dashboardStore.trendsData || []);
const getNewsTrendsData = () => {
  dashboardStore.getNewsTrendsData();
};
const chart = ref(null);
const circularPlot = ref(null);
let selectedData = ref({});
const displayedNews = ref([{title: "키워드를 선택해서", content: "추천 뉴스를 받아보세요."}]); // 표시할 뉴스 데이터

// Circular Barplot 렌더링 함수
const drawCircularBarplot = (data, offsetX = 0, id = "primary") => {
  const container = circularPlot.value.getBoundingClientRect();
  const width = container.width || 600;
  const height = container.height || 600;
  const innerRadius = 100;
  const outerRadius = Math.min(width, height) / 2 - 20;

  d3.select(circularPlot.value).select(`#${id}`).remove();
  const svg = d3
    .select(circularPlot.value)
    .append("svg")
    .attr("id", id)
    .attr("width", width + 300) // 범례 공간 추가
    .attr("height", height)
    .append("g")
    .attr(
      "transform",
      `translate(${width / 2 + offsetX}, ${height / 2})`
    );

  // X 축 (각도를 위한 스케일)
  const x = d3
    .scaleBand()
    .range([0, 2 * Math.PI])
    .domain(data.map((d) => d.name));

  // Y 축 (반지름 스케일)
  const y = d3.scaleLinear().range([innerRadius, outerRadius]).domain([0, 1]);

  // // 색상 스케일
  // const color = d3
  //   .scaleOrdinal()
  //   .range(["#4caf50", "#2196f3", "#ff9800", "#e91e63", "#9c27b0", "#00bcd4", "#ffc107", "#3f51b5"])
  //   .domain(data.map((d) => d.name));
  const color = d3.scaleOrdinal(d3.schemeCategory10).domain(data.map((d) => d.name));


  // Full value bar 추가 (투명도 처리)
  svg
    .append("g")
    .selectAll("path")
    .data(data)
    .join("path")
    .attr("fill", (d) => color(d.name))
    .attr("opacity", 0.2) // 투명도 처리
    .attr(
      "d",
      d3
        .arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius) // 최대치 반지름 사용
        .startAngle((d) => x(d.name))
        .endAngle((d) => x(d.name) + x.bandwidth())
        .padAngle(0.01)
        .padRadius(innerRadius)
    );

  // 실제 데이터 bar 추가
  svg
    .append("g")
    .selectAll("path")
    .data(data)
    .join("path")
    .attr("fill", (d) => color(d.name))
    .attr(
      "d",
      d3
        .arc()
        .innerRadius(innerRadius)
        .outerRadius((d) => y(d.value)) // 실제 값에 따라 반지름 조정
        .startAngle((d) => x(d.name))
        .endAngle((d) => x(d.name) + x.bandwidth())
        .padAngle(0.01)
        .padRadius(innerRadius)
    )
    .on("click", (event, d) => handleBarClick(d)); // 클릭 이벤트 추가

  svg
    .append("g")
    .selectAll("text")
    .data(data)
    .join("text")
    .attr("text-anchor", "middle")
    .attr("transform", (d) => {
      const angle = (x(d.name) + x.bandwidth() / 2); // 중심 각도
      const radius = y(d.value) + 30; // 막대 끝보다 약간 바깥쪽에 위치
      const xPos = Math.sin(angle) * radius;
      const yPos = -Math.cos(angle) * radius;
      return `translate(${xPos}, ${yPos})`; // x, y 좌표로 변환
    })
    .text((d) => `${(d.value * 100).toFixed(1)}%`) // 값에 100을 곱해 퍼센트로 표시
    .style("font-size", "20px")
    .style("fill", "#333");


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
    // 서버 요청
    const response = await axios.post(`${API_URL}/crawl/rec_news/`, {
      name: data.name, // 필요한 데이터를 요청에 포함
    });

// [  서버 리스폰스 형태
//   { "content": "첫 번째 뉴스 내용" },
//   { "content": "두 번째 뉴스 내용" },
//   { "content": "세 번째 뉴스 내용" }
// ]

    // 서버로부터 받은 데이터 처리
    if (response.status === 200 && response.data) {
      displayedNews.value = response.data.map((item, index) => ({
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
    // 오류 발생 시 기본 데이터를 표시하거나 사용자에게 알림
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

.circular-plot {
  width: 100%;
  height: 600px; /* Circular Plot의 높이 조정 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.details-container {
  width: 100%;
  max-height: 600px;
  overflow-y: auto; /* 스크롤 추가 */
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
}

.news-box h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.news-box p {
  font-size: 14px;
  color: #555;
}
</style>