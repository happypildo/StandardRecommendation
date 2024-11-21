<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const store = useUserStore()

const username = ref(null)
const password1 = ref(null)
const password2 = ref(null)

const signUp = function() {
  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value
  }
  store.signUp(payload)
}

</script>

<template>
  <div>
    <h1>회원가입</h1>
    <form @submit.prevent="signUp">
      <div>
        <label for="username">username: </label>
        <input type="text" id="username" v-model="username">
      </div>

      <div>
        <label for="password1">password1: </label>
        <input type="password" id="password1" v-model="password1">
      </div>

      <div>
        <label for="password2">password2: </label>
        <input type="password" id="password2" v-model="password2">
      </div>

      <input type="submit" value="회원가입">
    </form>
  </div>
</template>

<style scoped>

</style>