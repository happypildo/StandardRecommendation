<template>
  <div ref="chart" class="chart-container"></div>
</template>

<script setup>
import { ref, watch } from "vue";
import * as d3 from "d3";

// Props 선언
const props = defineProps({
  barData: {
    type: Array,
    required: true,
    default: () => [],
  },
});

// 그래프를 그릴 DOM 요소
const chart = ref(null);

// 막대 그래프를 그리는 함수
const drawBarChart = (data) => {
  if (!chart.value) {
    console.warn("chart element is not ready.");
    return;
  }

  // 컨테이너 크기 설정
  const container = chart.value.getBoundingClientRect();
  const width = container.width || 800;
  const height = container.height || 400;
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // 기존 그래프 제거
  d3.select(chart.value).select("svg").remove();

  // SVG 생성
  const svg = d3
    .select(chart.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // X축 스케일 (카테고리형 데이터)
  const xScale = d3
    .scaleBand()
    .domain(data.map((d) => d.label)) // 각 데이터의 label
    .range([0, innerWidth])
    .paddingInner(0.4) // 막대 간 간격
    .paddingOuter(0.2);

  // Y축 스케일 (값)
  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value)]) // 값의 최대치
    .range([innerHeight, 0]);

  // X축 추가
  svg
    .append("g")
    .attr("transform", `translate(0,${innerHeight})`) // X축 위치 설정
    .call(d3.axisBottom(xScale)) // X축 생성
    .selectAll("text")
    .attr("transform", "rotate(0)") // 텍스트 회전
    .style("text-anchor", "end"); // 텍스트 끝 정렬

  // Y축 추가
  svg.append("g").call(d3.axisLeft(yScale));

  // 막대 추가
  svg
    .selectAll(".bar")
    .data(data)
    .join("rect")
    .attr("class", "bar")
    .attr("x", (d) => xScale(d.label))
    .attr("y", innerHeight) // 처음에는 막대가 0 높이
    .attr("width", xScale.bandwidth())
    .attr("height", 0) // 처음에는 0으로 시작
    .attr("fill", "#69b3a2") // 기본 색상
    .transition() // 트랜지션 추가
    .duration(800)
    .attr("y", (d) => yScale(d.value))
    .attr("height", (d) => innerHeight - yScale(d.value));

  // 값 레이블 추가
  svg
    .selectAll(".label")
    .data(data)
    .join("text")
    .attr("class", "label")
    .attr("x", (d) => xScale(d.label) + xScale.bandwidth() / 2)
    .attr("y", (d) => yScale(d.value) - 5)
    .attr("text-anchor", "middle")
    .text((d) => d.value)
    .style("font-size", "12px")
    .style("fill", "#333");
};

// Props로 전달된 barData 변경 감지
watch(
  () => props.barData,
  (newData) => {
    console.log("BarGraph.vue: barData updated:", newData);
    if (chart.value && newData && newData.length) {
      drawBarChart(newData); // barData가 변경되면 새로 그래프를 그림
    } else {
      console.warn("No valid data for bar chart");
    }
  },
  { immediate: true } // 컴포넌트 초기 렌더링 시 실행
);
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}
</style>