<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
const store = useUserStore()

// 1. username, password 를 변수에 저장
//   -> 변수와 html input 태그를 양방향 바인딩
// JS 내부에서만 쓴다면 아래와 같이 선언
// let username = "test"

// 화면에 반영 + 변경 시 화면을 다시 그려야 한다면
//    ref 로 선언 및 정의
const username = ref('')
const password = ref('')

const logIn = function () {
  // console.log(username.value, password.value)
  // 서버로 요청을 보내도록 코드를 작성
  const payload = {
    username: username.value,
    password: password.value
  }
  store.logIn(payload)
}
</script>

<template>
  <div>
    <h1>로그인</h1>
    <!-- form 태그의 submit 이벤트: 자동으로 새로고침이 발생 -->
    <!-- @submit.prevent: 새로고침 이벤트 막아줌 -->
    <!-- prevent: 추가적인 이벤트를 막아주는 역할(preventDefault 와 같다) -->
    <form @submit.prevent="logIn">
      <div>
        <label for="username">username: </label>
        <!-- v-model: JS 변수와 html 쪽을 -->
        <!--      양방향으로 연결해주는 역할 -->
        <input type="text" id="username" v-model="username">
      </div>

      <div>
        <label for="password">password: </label>
        <input type="password" id="password" v-model="password">
      </div>

      <input type="submit" value="로그인">
    </form>
  </div>
</template>

<style scoped></style>