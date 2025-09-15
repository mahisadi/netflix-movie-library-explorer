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
    path: '/app/library',
    name: 'Library',
    component: ContentCurator
  },
  {
    path: '/app/insights',
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
  
  // Track page view only for Home and Library pages (exclude Insights)
  if (to.path === '/home' || to.path === '/app/library') {
    const pageName = enhancedMetricsService.getPageName(to.path)
    enhancedMetricsService.trackPageView(to.path, {
      page_name: pageName,
      full_url: window.location.href,
      referrer: from.path,
      navigation_type: 'router'
    })
  }
})

export default router
