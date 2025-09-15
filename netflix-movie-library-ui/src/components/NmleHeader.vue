<template>
  <header class="nmle-header">
    <div class="container">
      <div class="header-content">
        <div class="logo-section">
          <router-link 
            to="/home" 
            class="logo-link"
            @click="handleNavClick('Home', '/home')"
          >
            <div class="netflix-logo">
              <span class="netflix-text">NETFLIX</span>
              <img src="/nficon2023.ico" alt="Netflix" class="netflix-icon-mobile" />
            </div>
            <h1 class="app-title">Movie Library Explorer</h1>
          </router-link>
        </div>
        
        <nav class="main-navigation">
          <router-link 
            to="/home" 
            class="nav-link" 
            :class="{ active: $route.path === '/home' }"
            @click="handleNavClick('Home', '/home')"
          >
            <span class="nav-icon">🏠</span>
            <span class="nav-text">Home</span>
          </router-link>
        <router-link 
          to="/home/library" 
          class="nav-link" 
          :class="{ active: $route.path === '/home/library' }"
          @click="handleNavClick('Library', '/home/library')"
        >
          <span class="nav-icon">🎬</span>
          <span class="nav-text">Library</span>
        </router-link>
        <router-link 
          to="/home/insights" 
          class="nav-link" 
          :class="{ active: $route.path === '/home/insights' }"
          @click="handleNavClick('Insights', '/home/insights')"
        >
          <span class="nav-icon">📊</span>
          <span class="nav-text">Insights</span>
        </router-link>
        </nav>
        <div class="user-profile">
          <img 
            :src="userStore.user?.picture?.medium || '/default-avatar.svg'" 
            :alt="userStore.user?.name?.first || 'User'"
            class="profile-avatar"
          />
          <div class="profile-info" v-if="userStore.user">
            <span class="profile-name">{{ userStore.user.name.first }} {{ userStore.user.name.last }}</span>
            <span class="profile-location">{{ userStore.user.location.country }}</span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '../stores/userStore'
import { enhancedMetricsService } from '../services/enhancedMetricsService.js'

const userStore = useUserStore()

const handleNavClick = (pageName, pagePath) => {
  console.log('🖱️ Navigation Click:', { pageName, pagePath })
  
  // Track navigation click
  enhancedMetricsService.trackUserAction('navigation_click', {
    page: pagePath,
    page_name: pageName,
    click_type: 'navigation'
  })
}

onMounted(() => {
  if (!userStore.user) {
    userStore.fetchRandomUser()
  }
})
</script>

<style scoped>
.nmle-header {
  background-color: #000000;
  border-bottom: 1px solid #333;
  color: white;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.netflix-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: transparent;
  position: relative;
}

.netflix-text {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 32px;
  font-weight: 900;
  color: #e50914;
  letter-spacing: 1px;
  position: relative;
  display: inline-block;
  text-shadow: 
    0 1px 0 #b20710,
    0 2px 0 #8b0000,
    0 3px 0 #660000,
    0 4px 2px rgba(0, 0, 0, 0.8);
  transform: perspective(100px) rotateX(5deg);
  background: linear-gradient(180deg, #e50914 0%, #b20710 50%, #8b0000 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.netflix-icon-mobile {
  width: 24px;
  height: 24px;
  display: none;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.app-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: #e5e5e5;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-profile:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.profile-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #e50914;
  object-fit: cover;
  transition: all 0.3s ease;
}

.profile-avatar:hover {
  border-color: #ffffff;
  box-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.profile-name {
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}

.profile-location {
  color: #999;
  font-size: 0.8rem;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: row;
    gap: 0.5rem;
  }
  
  .logo-section {
    gap: 0.5rem;
  }
  
  .app-title {
    font-size: 0.7rem;
  }
  
  .netflix-logo {
    padding: 4px 8px;
  }
  
  .netflix-text {
    display: none;
  }
  
  .netflix-icon-mobile {
    display: block;
    width: 20px;
    height: 20px;
  }
  
  .user-profile {
    gap: 0.5rem;
  }
  
  .profile-info {
    display: none;
  }
  
  .profile-avatar {
    width: 30px;
    height: 30px;
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 0.6rem;
  }
  
  .netflix-icon-mobile {
    width: 18px;
    height: 18px;
  }
  
  .profile-avatar {
    width: 28px;
    height: 28px;
  }
}

@media (max-width: 360px) {
  .app-title {
    display: none;
  }
  
  .netflix-icon-mobile {
    width: 16px;
    height: 16px;
  }
  
  .profile-avatar {
    width: 26px;
    height: 26px;
  }
}

/* Navigation Styles */
.logo-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-link:hover {
  text-decoration: none;
  color: inherit;
}

.main-navigation {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: #ccc;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-icon {
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-text {
  font-size: 0.9rem;
  white-space: nowrap;
}

.nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  text-decoration: none;
}

.nav-link.active {
  color: #e50914;
  background: rgba(229, 9, 20, 0.1);
}

.nav-link.active:hover {
  color: #e50914;
  background: rgba(229, 9, 20, 0.2);
}

@media (max-width: 768px) {
  .main-navigation {
    gap: 0.5rem;
  }
  
  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .nav-text {
    display: none;
  }
  
  .nav-icon {
    font-size: 1.4rem;
  }
}

@media (max-width: 480px) {
  .nav-link {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
  }
  
  .nav-icon {
    font-size: 1.2rem;
  }
}

@media (max-width: 360px) {
  .nav-link {
    padding: 0.25rem 0.5rem;
  }
  
  .nav-icon {
    font-size: 1.1rem;
  }
}
</style>
