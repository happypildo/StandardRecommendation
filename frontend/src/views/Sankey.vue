<template>
  <div ref="chart" class="chart-container"></div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from "vue";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

import { useDashBoardStore } from "@/stores/dashboard";

// 클릭 이벤트 처리
// const getPlotImg = (series_num) => {
//     dashboardStore.getPlotImg(series_num);
// }
const getNetworkData = (series_num) => {
  dashboardStore.getNetworkData(series_num);
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
        // getPlotImg(lastWord);
        getNetworkData(lastWord);
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