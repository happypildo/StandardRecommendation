import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import axios from 'axios';

// CSRF 설정
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
// Vue 앱 생성 및 설정
const app = createApp(App);

// Pinia 플러그인 설정
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

// 토큰 복구 및 Axios 기본 헤더 설정
const token = localStorage.getItem('token');
if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`;
} else {
  console.warn('토큰이 존재하지 않습니다. 로그인이 필요합니다.');
}

// Axios 요청 함수 (사용 시 편의성을 위해 별도 함수 제공)
export const createBoard = async (data) => {
    try {
        const response = await axios.post('http://127.0.0.1:8000/api/v1/', data, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        console.log(response.data);
        return response.data;
    } catch (error) {
        console.error('게시글 작성 오류:', error.response || error);
        throw error; // 필요 시 호출부에서 에러 처리
    }
};

// 앱에 플러그인 적용
app.use(pinia);
app.use(router);

// 앱 마운트
app.mount('#app');
