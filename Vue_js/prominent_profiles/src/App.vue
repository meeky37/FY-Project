<template>
  <div id="app">
    <header>
      <div class="logo-container">
        <a href="/">
          <img v-if="!showLogoOnly" src="@/assets/profiles rework left align.png" alt="Logo"
               class="logo" />
          <img v-if="showLogoOnly" src="@/assets/profiles rework logo only.png" alt="Logo"
               class="logo" />
        </a>
      </div>
      <div class="centered-content">
        <EntitySelection />
      </div>
      <nav v-if="!showMenuIcon" class="original-nav">
        <router-link to="/about" class="nav-link">About</router-link>
        <router-link v-if="!authenticated" :to="''" class="nav-link"
                     @click="logonRedirect">Login </router-link>
        <router-link v-if="authenticated" :to="''" class="nav-link"  @click="logonRedirect"> Your
          Dashboard</router-link>
        <router-link v-if="authenticated" :to="''" class="nav-link"  @click="logout"> Logout
        </router-link>
      </nav>
      <router-link v-if="showMenuIcon" :to="{ name: 'menu' }" class="menu-link">Menu</router-link>
<!--      <img src="@/assets/hamburger-menu-icon.png" alt="Menu" class="menu-icon" />-->
    </header>

    <!-- Use keep-alive to persist the component across route changes -->
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
       <PageFooter/>
</template>
<script>
import { onMounted, onBeforeUnmount, computed, ref } from 'vue'
import { authenticated, checkAuthentication, logonRedirect, logout } from './shared_methods/auth_methods.js'
import EntitySelection from '@/components/EntitySelection.vue'
import PageFooter from '@/components/PageFooter.vue'

export default {
  components: {
    PageFooter,
    EntitySelection
  },

  setup () {
    const windowWidth = ref(window.innerWidth)

    const handleResize = () => {
      windowWidth.value = window.innerWidth
    }

    onMounted(() => {
      window.addEventListener('resize', handleResize)
      handleResize()
      checkAuthentication()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
    })

    const showMenuIcon = computed(() => windowWidth.value <= 950)
    const showLogoOnly = computed(() => windowWidth.value <= 950)

    return {
      authenticated,
      showMenuIcon,
      showLogoOnly,
      logonRedirect,
      logout
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: white;
  min-height: 100vh;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px;
  background:  #30d5c8;
  border-radius: 10px;
}

.logo {
  max-width: 30vw;
  max-height: 5vh;
  color: #2c3e50;
}

.logo-container {
  display: flex;
  align-items: center;
}

nav {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.nav-link {
  margin-right: 60px;
  font-weight: bold;
  font-size: 1.2rem;
  color: ghostwhite;
  text-decoration: none;
  transition: color 0.3s ease;
  border-radius: 5px;
}

.centered-content {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-right: 3vw;
}

.nav-link:hover {
  outline: 2px solid #fff;
  outline-offset:2px;
}

.menu-link {
  margin-right: 60px;
  font-weight: bold;
  font-size: 1.2rem;
  color: ghostwhite;
  text-decoration: none;
  transition: color 0.3s ease;
  border-radius: 5px;
}
</style>

<!--TBC if I replace with icon over "menu"-->
<!--.menu-icon {-->
<!--  width: 24px;-->
<!--  height: 24px;-->
<!--}-->
