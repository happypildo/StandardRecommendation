<template>
  <div class="chart-container">
    <div class="chart-item">
      <h2>(❁´◡`❁) 우와 - 내가 이렇게 통신에 관심이 많다니! (*/ω＼*)</h2>
      <p> ❤️❤️❤️ 최 강 통 신 네 트 워 크 ❤️❤️❤️ </p>
      <div ref="chart" class="network-graph"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";

import { useDashBoardStore } from "@/stores/dashboard";

// 네트워크 데이터 (노드와 링크 포함)
const dashboardStore = useDashBoardStore();
const networkData = computed(() => dashboardStore.networkData || { nodes: [], links: [] });

// 네트워크 그래프를 그릴 컨테이너
const chart = ref(null);

// 네트워크 그래프 렌더링 함수
const drawNetworkGraph = (data) => {
  const container = chart.value.getBoundingClientRect();
  const width = container.width || 800;
  const height = container.height || 600;

  // 기존 SVG 초기화
  d3.select(chart.value).select("svg").remove();

  // SVG 생성
  const svg = d3
    .select(chart.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // 색상 스케일
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  // 링크 두께 스케일 (가중치 기반)
  const linkWidthScale = d3
    .scaleLinear()
    .domain(d3.extent(data.links, (d) => d.weight)) // 가중치의 최소/최대값
    .range([1, 10]); // 링크 두께의 범위

  // Force Simulation 설정
  const simulation = d3
    .forceSimulation(data.nodes)
    .force(
      "link",
      d3.forceLink(data.links).id((d) => d.id).distance((d) => 100 / d.weight) // 가중치 기반 거리
    )
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .on("tick", ticked);

  // 링크 요소 추가
  const link = svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(data.links)
    .join("line")
    .attr("stroke-width", (d) => linkWidthScale(d.weight)) // 가중치 기반 두께 설정
    .attr("stroke", "#aaa");

  // 노드 요소 추가
  const node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(data.nodes)
    .join("circle")
    .attr("r", 10)
    .attr("fill", (d) => color(d.group))
    .call(
      d3
        .drag()
        .on("start", dragStarted)
        .on("drag", dragged)
        .on("end", dragEnded)
    );

  // 노드에 레이블 추가
  const label = svg
    .append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(data.nodes)
    .join("text")
    .attr("text-anchor", "middle")
    .attr("dy", -15)
    .text((d) => d.id)
    .style("font-size", "12px");

  // tick 이벤트 처리: 링크와 노드 위치 업데이트
  function ticked() {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

    label.attr("x", (d) => d.x).attr("y", (d) => d.y);
  }

  // 드래그 이벤트 처리
  function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
};

// 컴포넌트가 마운트될 때 네트워크 그래프 초기화
onMounted(() => {
  if (networkData.value?.nodes?.length && networkData.value?.links?.length) {
    drawNetworkGraph(networkData.value);
  }
});

// 데이터가 변경되었을 때 그래프 다시 렌더링
watch(networkData, (newData) => {
  if (newData?.nodes?.length && newData?.links?.length) {
    console.log("Network data updated:", newData);
    drawNetworkGraph(newData);
  } else {
    console.warn("No data to render network graph:", newData);
  }
});
</script>

<style scoped>
.network-graph {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background-color: #f9f9f9;
}
.chart-container {
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

</style>