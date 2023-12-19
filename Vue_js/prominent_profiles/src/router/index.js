import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
/* import EntitySelection from '../components/EntitySelection.vue' */
import EntityPage from '../views/EntityPage.vue'
import HomePage from '../views/HomePage.vue'
import ArticlePage from '../views/ArticlePage.vue'

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
