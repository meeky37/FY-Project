<template>
  <div id="app">
    <header>
      <div class="logo-container">
        <a href="/">
          <img src="@/assets/profiles rework left align.png" alt="Logo" class="logo" />
        </a>
      </div>
      <div class="centered-content">
        <EntitySelection />
      </div>
      <nav>
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/vue" class="nav-link">Vue</router-link>
        <router-link to="/about" class="nav-link">About</router-link>
        <router-link v-if="!authenticated" to="/login" class="nav-link">Login</router-link>
        <router-link v-if="authenticated" to="/dashboard" class="nav-link">Dashboard</router-link>
      </nav>
    </header>

    <!-- Use keep-alive to persist the component across route changes -->
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
import EntitySelection from '@/components/EntitySelection.vue'
</script>

<script>

export default {
  data () {
    return {
      authenticated: null
    }
  },
  created () {
    // Authentication status checked upon creation
    this.checkAuthentication()
  },
  methods: {
    checkAuthentication () {
      // TODO: API request or check a cookie/local storage here. VUEX worthwhile?
      this.authenticated = false
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
}

.logo {
  max-width: 20vw;
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
  transition: color 0.3s ease; /* Smooth transition effect */
  border-radius: 5px;
}

.centered-content {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-link:hover {
  outline: 2px solid #fff;
  outline-offset: 15px;
}
</style>
