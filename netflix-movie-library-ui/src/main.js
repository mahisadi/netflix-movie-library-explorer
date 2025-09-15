import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import enhancedMetricsService from './services/enhancedMetricsService'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize metrics service after Pinia is available
enhancedMetricsService.init()

app.mount('#app')
