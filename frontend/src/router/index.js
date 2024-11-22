// django 의 urls.py 역할
// 사용자가 특정 경로로 들어오면, 
// 해당하는 컴포넌트(페이지)를 출력해줄 수 있도록 설정해주는 파일
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import LogoutView from '@/views/LogoutView.vue'
import SignupView from '@/views/SignupView.vue'
import BoardCreateView from '@/views/BoardCreateView.vue'
import NewsView from '@/views/NewsViewer.vue'
import DashBoardView from '@/views/DashBoardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/logout',
      name: 'logout',
      component: LogoutView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },


    {
      path: '/create-board',
      name: 'createBorad',
      component: BoardCreateView,
    },

    {
      path: '/news',
      name: 'news',
      component: NewsView,
    },

    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashBoardView,
    },
  ],
})

export default router
