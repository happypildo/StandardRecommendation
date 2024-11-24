<template>
  <div ref="chart"></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "Heatmap",
  data() {
    return {
      matrix: [
        [6, 14, 8, 92, 14, 24, 47, 0, 15, 50],
        [92, 44, 68, 49, 17, 69, 11, 73, 22, 33],
        [42, 55, 98, 96, 28, 60, 14, 0, 43, 52],
        [79, 20, 59, 4, 11, 73, 98, 48, 90, 54],
        [91, 10, 29, 60, 1, 36, 17, 43, 38, 93],
        [41, 80, 51, 17, 22, 20, 9, 5, 34, 47],
        [32, 43, 68, 66, 95, 34, 23, 2, 21, 86],
        [60, 86, 82, 23, 31, 78, 25, 78, 3, 37],
        [67, 87, 71, 87, 83, 34, 72, 5, 0, 50],
        [69, 11, 7, 91, 3, 5, 35, 96, 77, 5],
      ],
      groupNames: [
        "Group 1",
        "Group 2",
        "Group 3",
        "Group 4",
        "Group 5",
        "Group 6",
        "Group 7",
        "Group 8",
        "Group 9",
        "Group 10",
      ],
    };
  },
  mounted() {
    this.drawHeatmap();
  },
  methods: {
    drawHeatmap() {
      const matrix = this.matrix;
      const groupNames = this.groupNames;

      const margin = { top: 50, right: 50, bottom: 50, left: 50 };
      const width = 600 - margin.left - margin.right;
      const height = 600 - margin.top - margin.bottom;

      const cellSize = width / groupNames.length;

      // SVG 설정
      const svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

      // 컬러 스케일 설정
      const colorScale = d3
        .scaleSequential()
        .interpolator(d3.interpolateBlues)
        .domain([0, d3.max(matrix.flat())]);

      // 행과 열 생성
      svg
        .selectAll("g")
        .data(matrix)
        .enter()
        .selectAll("rect")
        .data((row, i) => row.map((value, j) => ({ row: i, col: j, value })))
        .enter()
        .append("rect")
        .attr("x", (d) => d.col * cellSize)
        .attr("y", (d) => d.row * cellSize)
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("fill", (d) => colorScale(d.value))
        .append("title")
        .text((d) => `Value: ${d.value}`);

      // 행 이름 표시
      svg
        .append("g")
        .selectAll("text")
        .data(groupNames)
        .enter()
        .append("text")
        .attr("x", -10)
        .attr("y", (d, i) => i * cellSize + cellSize / 2)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text((d) => d);

      // 열 이름 표시
      svg
        .append("g")
        .selectAll("text")
        .data(groupNames)
        .enter()
        .append("text")
        .attr("x", (d, i) => i * cellSize + cellSize / 2)
        .attr("y", -10)
        .attr("dy", ".35em")
        .style("text-anchor", "middle")
        .text((d) => d);
    },
  },
};
</script>

<style>
/* 히트맵 스타일 (선택 사항) */
</style>