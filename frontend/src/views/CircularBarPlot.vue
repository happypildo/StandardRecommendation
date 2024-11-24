<template>
  <div ref="chart" class="chart-container">
    <!-- Circular Barplot -->
    <div ref="circularPlot" class="circular-plot"></div>
    <!-- Line Plot -->
    <div ref="linePlot" class="line-plot"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import axios from "axios";
import { useDashBoardStore } from "@/stores/dashboard";

const dashboardStore = useDashBoardStore();
const trendsData = computed(() => dashboardStore.trendsData || []);
const getNewsTrendsData = () => {
  dashboardStore.getNewsTrendsData();
};
const API_URL = "http://127.0.0.1:8000";

const chart = ref(null);
const circularPlot = ref(null);
const linePlot = ref(null);
let selectedData = ref(null); // 클릭한 데이터 저장

// Circular Barplot 렌더링 함수
const drawCircularBarplot = (data, offsetX = 0, id = "primary") => {
  const container = circularPlot.value.getBoundingClientRect();
  const width = container.width || 600;
  const height = container.height || 600;
  const innerRadius = 100;
  const outerRadius = Math.min(width, height) / 2 - 20;

  // 기존 그래프 제거
  d3.select(circularPlot.value).select(`#${id}`).remove();

  // SVG 생성
  const svg = d3
    .select(circularPlot.value)
    .append("svg")
    .attr("id", id) // ID로 그래프 구분
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr(
      "transform",
      `translate(${width / 2 + offsetX}, ${height / 2})`
    );

  // 각도 계산을 위한 X 축 스케일
  const x = d3
    .scaleBand()
    .range([0, 2 * Math.PI])
    .domain(data.map((d) => d.name));

  // 막대 길이를 위한 Y 축 스케일
  const y = d3.scaleLinear().range([innerRadius, outerRadius]).domain([0, 1]);

  // 색상 스케일
  const color = d3
    .scaleOrdinal()
    .range([
      "#4caf50",
      "#2196f3",
      "#ff9800",
      "#e91e63",
      "#9c27b0",
      "#00bcd4",
      "#ffc107",
      "#3f51b5",
    ])
    .domain(data.map((d) => d.name));

  // 막대 추가
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
        .outerRadius((d) => y(d.value))
        .startAngle((d) => x(d.name))
        .endAngle((d) => x(d.name) + x.bandwidth())
        .padAngle(0.01)
        .padRadius(innerRadius)
    )
    .on("click", (event, d) => handleBarClick(d)); // 클릭 이벤트 추가

  // 이름 라벨 추가
  svg
    .append("g")
    .selectAll("text")
    .data(data)
    .join("text")
    .attr("text-anchor", "middle")
    .attr("transform", (d) => {
      const angle = (x(d.name) + x.bandwidth() / 2) * (180 / Math.PI) - 90;
      const radius = outerRadius + 20;
      return `rotate(${angle}) translate(${radius}, 0)`;
    })
    .text((d) => d.name)
    .style("font-size", "12px")
    .style("fill", "#333");
};

// 클릭 이벤트 처리
const handleBarClick = async (d) => {
  console.log(`Clicked on bar: ${d.name} with value: ${d.value}`);
  selectedData.value = d; // 클릭된 데이터 저장

  // Circular Barplot을 왼쪽으로 이동 (절대 위치로 변경)
  const circularPlotWidth = circularPlot.value.getBoundingClientRect().width;
  d3.select(circularPlot.value)
    .transition()
    .duration(500)
    // .style("transform", `translate(-${circularPlotWidth / 8}px, 0)`);

  // 새로운 데이터를 가져와 Line Plot 그리기
  const newData = await generateSecondaryData(d);
  if (newData && newData.length > 0) {
    drawLinePlot(newData); // Line Plot 생성
  } else {
    console.error("No data received for Line Plot");
  }
};

// 클릭된 데이터 기반으로 새 데이터 생성
const generateSecondaryData = async (clickedData) => {
  try {
    const response = await axios.get(
      `${API_URL}/crawl/lineplot/${clickedData.name}/`
    );
    if (response.status === 200) {
      console.log("Data fetched successfully:", response.data);
      return response.data;
    } else {
      console.error(
        "Error fetching data:",
        response.status,
        response.statusText
      );
      return [];
    }
  } catch (error) {
    console.error("Error occurred while fetching data:", error);
    return [];
  }
};

// Line Plot 그리기
const drawLinePlot = (data) => {
  if (!linePlot.value) return;

  const container = linePlot.value.getBoundingClientRect();
  const width = container.width || 600;
  const height = container.height || 600; // container 높이를 기준으로 설정
  const margin = { top: 50, right: 50, bottom: 50, left: 50 };
  // const container = linePlot.value.getBoundingClientRect();
  // const width = container.width || 600;
  // const height = 300;

  // 기존 Line Plot 제거
  d3.select(linePlot.value).select("svg").remove();

  // SVG 생성
  const svg = d3
    .select(linePlot.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .style("background-color", "#f9f9f9");

  // X 축 스케일 (user_id 기준)
  const x = d3
    .scalePoint()
    .domain(data.map((d) => d.user_id))
    .range([50, width - 50]);

  // Y 축 스케일 (total_clicks 기준)
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.total_clicks)])
    .range([height - 50, 50]);

  // X 축 추가
  svg
    .append("g")
    .attr("transform", `translate(0, ${height - 50})`)
    .call(d3.axisBottom(x).tickFormat((d) => `User ${d}`));

  // Y 축 추가
  svg.append("g").attr("transform", "translate(50, 0)").call(d3.axisLeft(y));

  // 선 추가
  const line = d3
    .line()
    .x((d) => x(d.user_id))
    .y((d) => y(d.total_clicks))
    .curve(d3.curveMonotoneX);

  svg
    .append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "#2196f3")
    .attr("stroke-width", 2)
    .attr("d", line);

  // 점 추가
  svg
    .selectAll("circle")
    .data(data)
    .join("circle")
    .attr("cx", (d) => x(d.user_id))
    .attr("cy", (d) => y(d.total_clicks))
    .attr("r", 5)
    .attr("fill", (d) => (d.is_current_user ? "#ff5722" : "#4caf50"))
    .attr("stroke", "#333")
    .attr("stroke-width", 1.5);
};

// 컴포넌트 마운트 시 Circular Barplot 렌더링
onMounted(() => {
  getNewsTrendsData();
  if (trendsData.value.length) {
    drawCircularBarplot(trendsData.value, 0, "primary");
  }
});

// 데이터 변경 시 Circular Barplot 업데이트
watch(trendsData, (newData) => {
  if (newData.length) {
    drawCircularBarplot(newData, 0, "primary");
  }
});
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  min-height: 500px;
  background-color: #f9f9f9;
  position: relative;
}

.circular-plot {
  flex: 1;
  transition: transform 0.5s ease;
}

.line-plot {
  flex: 1;
  padding-left: 20px;
}
</style>