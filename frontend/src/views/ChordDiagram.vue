<template>
  <div ref="chart"></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "ChordDiagram",
  props: {
    matrix: {
      type: Array,
      required: true,
    },
    groupNames: {
      type: Array,
      required: true,
    },
  },
  mounted() {
    this.drawChordDiagram();
  },
  methods: {
    drawChordDiagram() {
      const matrix = this.matrix;
      const groupNames = this.groupNames;

      const width = 600;
      const height = 600;
      const innerRadius = Math.min(width, height) * 0.4;
      const outerRadius = innerRadius + 10;

      // SVG 설정
      const svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

      // Chord 레이아웃 생성
      const chord = d3
        .chord()
        .padAngle(0.05) // 그룹 간 간격
        .sortSubgroups(d3.descending); // 서브그룹 정렬

      const chords = chord(matrix);

      // 그룹 아크 생성
      const arc = d3
        .arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

      svg
        .append("g")
        .selectAll("g")
        .data(chords.groups)
        .join("g")
        .append("path")
        .attr("fill", (d, i) => d3.schemeCategory10[i])
        .attr("d", arc)
        .append("title")
        .text((d, i) => `${groupNames[i]}: ${d.value}`);

      // Chord 경로 생성
      const ribbon = d3.ribbon().radius(innerRadius);

      svg
        .append("g")
        .selectAll("path")
        .data(chords)
        .join("path")
        .attr("fill", (d) => d3.schemeCategory10[d.target.index])
        .attr("stroke", "black")
        .attr("d", ribbon)
        .append("title")
        .text(
          (d) =>
            `${groupNames[d.source.index]} → ${groupNames[d.target.index]}: ${d.source.value}`
        );
    },
  },
};
</script>

<style>
/* 스타일 추가(선택 사항) */
</style>