import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EntityPage from '../views/EntityPage.vue'
import HomePage from '../views/HomePage.vue'
import ArticlePage from '../views/ArticlePage.vue'
import LoginPage from '../views/LoginPage.vue'
import SignUpPage from '../views/SignUpPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import MenuPage from '@/views/MenuPage.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import ResetPassword from '@/views/ResetPassword.vue'

const routes = [
  {
    path: '/vue',
    name: 'vue_home',
    component: HomeView
  },
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/about',
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/forgot-password',
    name: 'forgotPassword',
    component: ForgotPassword
  },
  {
    path: '/reset-password',
    name: 'resetPassword',
    component: ResetPassword
  },
  {
    path: '/sign-up',
    name: 'signUp',
    component: SignUpPage
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardPage
  },
  {
    path: '/menu',
    name: 'menu',
    component: MenuPage
  },

  // Dynamic routing for entity pages
  {
    path: '/entity/:id',
    name: 'entity',
    component: EntityPage
  },
  {
    path: '/article/:entityId/:articleId',
    name: 'entryId',
    component: ArticlePage,
    props: route => ({
      entityId: route.params.entityId,
      articleId: route.params.articleId
    })
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
