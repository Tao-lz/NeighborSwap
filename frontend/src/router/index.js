import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PublishView from '../views/PublishView.vue'
import MineView from '../views/MineView.vue'
import DashboardView from '../views/DashboardView.vue'
import ItemDetailView from '../views/ItemDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/publish', name: 'publish', component: PublishView },
    { path: '/mine', name: 'mine', component: MineView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/item/:id', name: 'item-detail', component: ItemDetailView },
  ],
})

export default router
