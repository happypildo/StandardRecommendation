<!-- <template>
  <div ref="chart"></div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from "vue";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

import { useDashBoardStore } from "@/stores/dashboard";

// 클릭 이벤트 처리
const getPlotImg = (series_num) => {
    dashboardStore.getPlotImg(series_num);
}

const chart = ref(null); // Sankey 그래프가 그려질 DOM 요소 참조
const dashboardStore = useDashBoardStore();
const data = computed(() => dashboardStore.sankeyData);

// 유니크한 ID를 생성하는 함수
const generateId = (index) => `gradient-${index}`;

// Sankey Diagram 렌더링 함수
const drawSankeyDiagram = (data) => {
  // const width = 500;
  // const height = 700;
  // const margin = { top: 10, right: 200, bottom: 30, left: 200 };
  const container = chart.value.getBoundingClientRect();
  const width = container.width * 0.8; // 컨테이너 너비의 80%
  const height = container.height * 0.9; // 컨테이너 높이의 90%
  const margin = {
    top: height * 0.05, // 높이의 5%를 위쪽 여백으로
    right: width * 0.2, // 너비의 20%를 오른쪽 여백으로
    bottom: height * 0.05, // 높이의 5%를 아래쪽 여백으로
    left: width * 0.2, // 너비의 20%를 왼쪽 여백으로
  };
  console.log(height, width)

  // 기존 그래프 초기화
  d3.select(chart.value).select("svg").remove();

  // SVG 생성
  const svg = d3
    .select(chart.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Sankey 레이아웃 정의
  const { nodes, links } = sankey()
    .nodeWidth(20)
    .nodePadding(10)
    .size([width, height])(data);

  // 색상 스케일 정의
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  // SVG에 그라데이션 정의
  const defs = svg.append("defs");
  nodes.forEach((node, i) => {
    const gradientId = generateId(i);
    const gradient = defs
      .append("linearGradient")
      .attr("id", gradientId)
      .attr("x1", "0%")
      .attr("x2", "100%")
      .attr("y1", "0%")
      .attr("y2", "0%");

    gradient
      .append("stop")
      .attr("offset", "0%")
      .attr("stop-color", color(i))
      .attr("stop-opacity", 0.8);

    gradient
      .append("stop")
      .attr("offset", "100%")
      .attr("stop-color", d3.rgb(color(i)).brighter(1.5))
      .attr("stop-opacity", 0.8);
  });

  // 노드(Node) 그리기
  const nodeGroup = svg.append("g").selectAll("rect").data(nodes).join("g");

  nodeGroup
    .append("rect")
    .attr("x", (d) => d.x0)
    .attr("y", (d) => d.y0)
    .attr("width", (d) => d.x1 - d.x0)
    .attr("height", (d) => d.y1 - d.y0)
    .attr("fill", (d, i) => `url(#${generateId(i)})`)
    .on("click", (event, d) => {
      // 노드 클릭 이벤트
      console.log(`Clicked on node: ${d.name}`);
      d3.selectAll("rect").attr("stroke", null); // 모든 노드 초기화
      d3.select(event.target)
        .attr("stroke", "orange")
        .attr("stroke-width", 3); // 클릭된 노드 강조
      

      const str = d.name;
      if (str.includes("Series")) { 
        const words = str.split(" "); 
        const lastWord = words[words.length - 1]; 
        console.log(lastWord); 
        getPlotImg(lastWord);
}
    })
    .append("title")
    .text((d) => `${d.name}\n${d.value}`);

  // 노드 이름(Label) 추가
  nodeGroup
    .append("text")
    .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6))
    .attr("y", (d) => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
    .text((d) => d.name)
    .style("font-size", "12px")
    .style("fill", "#333");

  // 링크 그리기
  svg
    .append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("fill", "none")
    .attr("stroke", (d) => `url(#${generateId(d.source.index)})`)
    .attr("stroke-width", (d) => Math.max(1, d.width))
    .style("mix-blend-mode", "multiply")
    .on("click", (event, d) => {
      // 링크 클릭 이벤트
      console.log(`Clicked on link: ${d.source.name} → ${d.target.name}`);
      d3.selectAll("path").style("opacity", 0.3); // 모든 링크 비활성화
      d3.select(event.target).style("opacity", 1).attr("stroke", "red"); // 클릭된 링크 강조
    })
    .append("title")
    .text((d) => `${d.source.name} → ${d.target.name}\n${d.value}`);

  // 범례(Legend) 추가
  const legend = svg
    .append("g")
    .attr("transform", `translate(${width + 20}, 20)`);

  nodes.forEach((node, i) => {
    const legendGroup = legend.append("g").attr("transform", `translate(0, ${i * 20})`);

    legendGroup
      .append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .attr("fill", `url(#${generateId(i)})`);

    legendGroup
      .append("text")
      .attr("x", 20)
      .attr("y", 12)
      .text(node.name)
      .style("font-size", "12px")
      .style("fill", "#333");
  });
};

// 데이터 변화를 감지하여 Sankey Diagram 업데이트
watch(data, (newData) => {
  drawSankeyDiagram(newData);
});
</script>

<style>
/* 스타일 정의 */
div[ref="chart"] {
  margin: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

svg {
  font-family: Arial, sans-serif;
}
</style> -->
<template>
  <div ref="chart" class="chart-container"></div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from "vue";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

import { useDashBoardStore } from "@/stores/dashboard";

// 클릭 이벤트 처리
const getPlotImg = (series_num) => {
    dashboardStore.getPlotImg(series_num);
}

// Sankey 데이터와 참조
const chart = ref(null); // 다이어그램 컨테이너 참조
const dashboardStore = useDashBoardStore();
const data = computed(() => dashboardStore.sankeyData || { nodes: [], links: [] });

// 유니크한 ID 생성
const generateId = (index) => `gradient-${index}`;

// Sankey 다이어그램 렌더링 함수
const drawSankeyDiagram = (data) => {
  const container = chart.value.getBoundingClientRect();
  const width = container.width || 700; // 부모 컨테이너 너비
  const height = (container.height || 500) * 0.8; // 부모 컨테이너 높이
  
  const margin = {
    top: height * 0.05,
    right: width * 0.1,
    bottom: height * 0.05,
    left: width * 0.1,
  };

  // 기존 SVG 초기화
  d3.select(chart.value).select("svg").remove();

  const svg = d3
    .select(chart.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  const { nodes, links } = sankey()
    .nodeWidth(20)
    .nodePadding(15)
    .size([width - margin.left - margin.right, height - margin.top - margin.bottom])(data);

  const color = d3.scaleOrdinal(d3.schemeCategory10);

  // 노드 그리기
  const nodeGroup = svg.append("g").selectAll("rect").data(nodes).join("g");

  nodeGroup
    .append("rect")
    .attr("x", (d) => d.x0)
    .attr("y", (d) => d.y0)
    .attr("width", (d) => d.x1 - d.x0)
    .attr("height", (d) => d.y1 - d.y0)
    .attr("fill", (d, i) => color(i))
    .on("click", (event, d) => {
      // 노드 클릭 이벤트
      console.log(`Clicked on node: ${d.name}`);
      d3.selectAll("rect").attr("stroke", null); // 모든 노드 초기화
      d3.select(event.target)
        .attr("stroke", "orange")
        .attr("stroke-width", 3); // 클릭된 노드 강조
      

      const str = d.name;
      if (str.includes("Series")) { 
        const words = str.split(" "); 
        const lastWord = words[words.length - 1]; 
        console.log(lastWord); 
        getPlotImg(lastWord);
      }
    })
    .append("title")
    .text((d) => `${d.name}\n${d.value}`);

  nodeGroup
    .append("text")
    .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6))
    .attr("y", (d) => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
    .text((d) => d.name)
    .style("font-size", "12px")
    .style("fill", "#333");

  // 링크 그리기
  svg
    .append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("fill", "none")
    .attr("stroke", (d) => color(d.source.index))
    .attr("stroke-width", (d) => Math.max(1, d.width))
    .style("opacity", 0.7)
    .on("click", (event, d) => {
      // 링크 클릭 이벤트 처리
      console.log(`Clicked on link: ${d.source.name} → ${d.target.name}`);
      d3.selectAll("path").style("opacity", 0.3); // 모든 링크 비활성화
      d3.select(event.target).style("opacity", 1).attr("stroke", "red"); // 클릭된 링크 강조
    })
    .append("title")
    .text((d) => `${d.source.name} → ${d.target.name}\n${d.value}`);
};

// 데이터 변경 감지 및 업데이트
watch(data, (newData) => {
  if (newData?.nodes?.length && newData?.links?.length) {
    drawSankeyDiagram(newData);
  }
});

// 마운트 시 초기화
onMounted(() => {
  if (data.value?.nodes?.length && data.value?.links?.length) {
    drawSankeyDiagram(data.value);
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 500px; /* 최소 높이 설정 */
}
</style>