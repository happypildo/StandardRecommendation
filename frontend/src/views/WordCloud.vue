<template>
  <div class="word-cloud" ref="wordCloud"></div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useDashBoardStore } from "@/stores/dashboard"; // Pinia 스토어 가져오기
import cloud from "d3-cloud";
import * as d3 from "d3";

// Pinia 스토어 인스턴스 가져오기
const dashboardStore = useDashBoardStore();

// Refs
const wordCloud = ref(null);

// 워드클라우드 업데이트 메서드
const updateWordCloud = (words) => {
    d3.select(wordCloud.value).selectAll("*").remove(); // 기존 SVG 제거

    const layout = cloud()
        .size([500, 500]) // 워드클라우드 크기
        .words(
        words.map((word) => ({
            text: word.text,
            size: word.size,
        }))
        )
        .padding(5) // 단어 간격
        .rotate(() => (Math.random() > 0.5 ? 0 : 90)) // 회전 각도
        .fontSize((d) => d.size) // 폰트 크기
        .on("end", renderWords);

    layout.start();
};

// 단어 렌더링 메서드
const renderWords = (words) => {
  const svg = d3
    .select(wordCloud.value)
    .append("svg")
    .attr("width", 500)
    .attr("height", 500)
    .append("g")
    .attr("transform", "translate(250,250)");

  svg
    .selectAll("text")
    .data(words)
    .enter()
    .append("text")
    .style("font-size", (d) => `${d.size}px`)
    .style("fill", () =>
      d3.schemeCategory10[Math.floor(Math.random() * 10)]
    )
    .attr("text-anchor", "middle")
    .attr("transform", (d) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
    .text((d) => d.text);
};

// Pinia 스토어의 words 데이터를 감시
watch(
  () => dashboardStore.wordClouds,
  (newWords) => {
    updateWordCloud(newWords); // 데이터 변경 시 업데이트
    // renderWords(newWords);
  },
  { deep: true, immediate: true } // 객체 내부 변경 감지 및 초기 실행
);
</script>

<style scoped>
.word-cloud {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
}
</style>
