// import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const token = localStorage.getItem('token');

const axiosInstance = axios.create({
    headers: {
      'Authorization': `Token ${token}`
    }
  });
  
// 이 인스턴스를 사용하여 요청을 보내세요
// axiosInstance.post('/api/boards/6/comment/', commentData);

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// app.use(createPinia())
app.use(pinia)
app.use(router)

app.mount('#app')
