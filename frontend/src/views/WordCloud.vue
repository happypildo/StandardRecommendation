<template>
  <div class="word-cloud" ref="wordCloud"></div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useDashBoardStore } from "@/stores/dashboard";
import cloud from "d3-cloud";
import * as d3 from "d3";

const dashboardStore = useDashBoardStore();
const wordCloud = ref(null);

const updateWordCloud = (words) => {
  const container = wordCloud.value.getBoundingClientRect();
  const width = container.width || 500;
  const height = container.height || 500;

  d3.select(wordCloud.value).selectAll("*").remove();

  const layout = cloud()
    .size([width, height])
    .words(
      words.map((word) => ({
        text: word.text,
        size: word.size,
      }))
    )
    .padding(2)
    .rotate(() => (Math.random() > 0.5 ? 0 : 90))
    .fontSize((d) => d.size)
    .on("end", (generatedWords) => renderWords(generatedWords, width, height));

  layout.start();
};

const renderWords = (words, width, height) => {
  const svg = d3
    .select(wordCloud.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`);

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




watch(
  () => dashboardStore.wordClouds,
  (newWords) => {
    if (newWords && newWords.length > 0) {
      updateWordCloud(newWords);
    }
  },
  { deep: true, immediate: true }
);
</script>

<style scoped>
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
