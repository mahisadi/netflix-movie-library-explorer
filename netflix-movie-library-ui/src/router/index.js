import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ContentCurator from '../views/ContentCurator.vue'
import Insights from '../views/Insights.vue'
import { enhancedMetricsService } from '../services/enhancedMetricsService.js'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/home/library',
    name: 'Library',
    component: ContentCurator
  },
  {
    path: '/home/insights',
    name: 'Insights',
    component: Insights
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Track page views on navigation
router.afterEach((to, from) => {
  console.log('🔄 Router Navigation:', {
    from: from.path,
    to: to.path,
    name: to.name
  })
  
  // Track page view
  enhancedMetricsService.trackPageView(to.path, {
    page_name: to.name,
    full_url: window.location.href,
    referrer: from.path,
    navigation_type: 'router'
  })
})

export default router
