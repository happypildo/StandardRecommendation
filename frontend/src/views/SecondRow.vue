<template>
  <div class="chart-container">
    <!-- 설명 1 -->
    <div class="chart-item">
      <h2>🙄 내 관심도와 통신 사이의 연-결-⭐️ (*/ω＼*)</h2>
      <p> ❤️❤️❤️ 우측 노드를 선택해 더 상세한 나와 통신의 연결고리를 확인해보자! ❤️❤️❤️ </p>
      <div ref="chart" class="sankey-container"></div>
    </div>

    <!-- 설명 2 -->
    <div class="chart-item">
      <h2>🔑 내 관심도 😘</h2>
      <div class="word-cloud" ref="wordCloud"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from "vue";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";
import cloud from "d3-cloud";

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
  const width = container.width || 700;
  const height = (container.height || 500) * 0.8;

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
    .style("opacity", 0.4)
    .on("click", (event, d) => {
      // 링크 클릭 이벤트 처리
      console.log(`Clicked on link: ${d.source.name} → ${d.target.name}`);
      d3.selectAll("path").style("opacity", 0.3); // 모든 링크 비활성화
      d3.select(event.target).style("opacity", 1).attr("stroke", "red"); // 클릭된 링크 강조
    })
    .append("title")
    .text((d) => `${d.source.name} → ${d.target.name}\n${d.value}`);

// 각 노드에 이름 추가 (두 줄 처리 포함)
nodeGroup
  .append("text")
  .attr("x", (d) => (d.x0 < width / 2 ? d.x0 - 10 : d.x1 + 10)) // 왼쪽/오른쪽 결정
  .attr("y", (d) => (d.y0 + d.y1) / 2 - 5) // 노드 중앙에 배치
  .attr("text-anchor", (d) => (d.x0 < width / 2 ? "end" : "start")) // 텍스트 정렬
  .style("font-size", "12px")
  .style("fill", "#333")
  .each(function (d) {
    const textElement = d3.select(this);
    const nameParts = d.name.split(" "); // 공백으로 문자열 분리

    // Source 노드의 경우만 두 줄로 표시
    if (d.x0 < width / 2) {
      // 문자열을 반으로 나누기
      const middleIndex = Math.ceil(nameParts.length / 2);
      const firstLine = nameParts.slice(0, middleIndex).join(" "); // 첫 줄
      const secondLine = nameParts.slice(middleIndex).join(" "); // 두 번째 줄

      // 첫 번째 줄 추가
      textElement
        .append("tspan")
        .text(firstLine)
        .attr("x", d.x0 - 10) // 줄마다 동일한 x 좌표
        .attr("dy", "0.35em"); // 첫 줄 위치

      // 두 번째 줄 추가
      textElement
        .append("tspan")
        .text(secondLine)
        .attr("x", d.x0 - 10) // 줄마다 동일한 x 좌표
        .attr("dy", "1.2em"); // 두 번째 줄은 아래로 이동
    } else {
      // Target 노드는 한 줄로 표시
      textElement.text(d.name);
    }
  });
};

const wordCloud = ref(null);

const updateWordCloud = (words) => {
  // DOM 참조 유효성 확인
  if (!wordCloud.value) {
    console.warn("wordCloud element is not available.");
    return;
  }

  const container = wordCloud.value.getBoundingClientRect();
  const width = container.width || 500;
  const height = container.height || 500;

  // 기존 워드 클라우드 초기화
  d3.select(wordCloud.value).selectAll("*").remove();

  const maxFontSize = Math.min(width, height) / 10; // 최대 폰트 크기 제한

  // d3-cloud 레이아웃 설정
  const layout = cloud()
    .size([width, height])
    .words(
      words.map((word) => ({
        text: word.text,
        size: Math.min(word.size, maxFontSize), // 최대 폰트 크기 제한 적용
      }))
    )
    .padding(2)
    .rotate(() => (Math.random() > 0.5 ? 0 : 90))
    .fontSize((d) => d.size)
    .on("end", (generatedWords) => {
      // 유효한 DOM 상태에서만 렌더링
      if (wordCloud.value) {
        renderWords(generatedWords, width, height);
      } else {
        console.warn("wordCloud element is no longer available during render.");
      }
    });

  layout.start();
};

const renderWords = (words, width, height) => {
  const svg = d3
    .select(wordCloud.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`); // 중심에 배치

  const fontScale = Math.min(width, height) / 500; // 글자 크기 비율 조정

  svg
    .selectAll("text")
    .data(words)
    .enter()
    .append("text")
    .style("font-size", (d) => `${d.size * fontScale}px`) // 크기 스케일링
    .style("fill", () =>
      d3.schemeCategory10[Math.floor(Math.random() * 10)]
    )
    .attr("text-anchor", "middle")
    .attr("transform", (d) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
    .text((d) => d.text);
};


watch(
  () => dashboardStore.wordClouds,
  (newWords) => {
    if (newWords && newWords.length > 0) {
      updateWordCloud(newWords);
    }
  },
  { deep: true, immediate: true }
);

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
    updateWordCloud(dashboardStore.wordClouds);
  }
});
</script>

<style scoped>
.chart-container {
  display: grid; /* 2x2 구조를 만들기 위해 grid 사용 */
  grid-template-columns: 7fr 3fr; /* 두 열로 나눔 */
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

.sankey-container {
  width: 100%;
  height: 100%;
  min-height: 500px; /* 최소 높이 설정 */
}

.word-cloud {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>