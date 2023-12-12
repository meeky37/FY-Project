import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EntityOverview from '../components/EntitySelection.vue'
import EntityPage from '../views/EntityPage.vue'

const routes = [
  {
    path: '/vue',
    name: 'vue_home',
    component: HomeView
  },
  {
    path: '/',
    name: 'home',
    component: EntityOverview
  },
  {
    path: '/about',
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  // Dynamic routing for entity pages
  {
    path: '/entity/:id',
    name: 'entity',
    component: EntityPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
