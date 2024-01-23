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
<!--        <router-link to="/" class="nav-link">Home</router-link>-->
<!--        <router-link to="/vue" class="nav-link">Vue</router-link>-->
        <router-link to="/about" class="nav-link">About</router-link>
        <router-link v-if="!authenticated" :to="''" class="nav-link"
                     @click="LogonRedirect">Login </router-link>
        <router-link v-if="authenticated" :to="''" class="nav-link"  @click="LogonRedirect"> Your
          Dashboard</router-link>
        <router-link v-if="authenticated" :to="''" class="nav-link"  @click="Logout"> Logout
        </router-link>
      </nav>
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
import VueCookies from 'vue-cookie'
import router from '@/router'
import EntitySelection from '@/components/EntitySelection.vue'
import { API_BASE_URL } from '@/config'
import axios from 'axios'
import PageFooter from '@/components/PageFooter.vue'
import { checkAuthenticationCommon } from '@/auth.js'

export default {
  components: {
    PageFooter,
    EntitySelection
  },

  data () {
    return {
      authenticated: null
    }
  },

  beforeMount () {
    this.checkAuthentication()
  },

  watch: {
    // LoginPage.vue redirects to dashboard on successful login - this is implemented to
    // update the header to 'Your Dashboard' immediately
    $route (to, from) {
      if (to.path === '/dashboard') {
        this.checkAuthentication()
      }
    }
  },
  methods: {
    // async checkAuthentication () {
    //   // TODO: API request or check a cookie/local storage here. VUEX worthwhile?
    //   const accessToken = VueCookies.get('access_token')
    //
    //   if (!accessToken) {
    //     // Attempt to refresh the access token using the refresh token
    //     const refreshToken = VueCookies.get('refresh_token')
    //     if (refreshToken) {
    //       try {
    //         const response = await axios.post(`${API_BASE_URL}/accounts/api/token/refresh/`, {
    //           refresh: refreshToken
    //         })
    //         // Update the access token cookie
    //         VueCookies.set('access_token', response.data.access)
    //         const accessToken = VueCookies.get('access_token')
    //         this.authenticated = !!accessToken
    //         return
    //       } catch (refreshError) {
    //         // If refresh fails, redirect to the login page.
    //         console.error('Token refresh failed', refreshError)
    //         router.push('/login')
    //       }
    //     }
    //   }
    //   this.authenticated = !!accessToken
    // },

    async checkAuthentication () {
      try {
        const isAuthenticated = await checkAuthenticationCommon()
        this.authenticated = isAuthenticated
      } catch (error) {
        console.error('Error checking authentication:', error)
        // If refresh has failed in checkAuthenticationCommon, redirect to the login page.
        router.push('/login')
      }
    },

    async LogonRedirect () {
      await this.checkAuthentication()
      if (this.authenticated) {
        this.$router.push('/dashboard/')
      } else {
        this.$router.push('/login/')
      }
    },

    Logout () {
      VueCookies.delete('access_token')
      VueCookies.delete('refresh_token')

      const csrfToken = VueCookies.get('csrftoken')

      // Redirect to dashboard which will trigger update of header + redirect to login page
      axios.post(`${API_BASE_URL}/accounts/logout/`, null, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken
        }
      })
        .then(() => {
          // Redirect to the desired page after successful logout
          this.authenticated = false
          // router.push('/dashboard/')
          this.LogonRedirect()
        })
        .catch(error => {
          console.error('Error during logout:', error)
        })
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
  transition: color 0.3s ease;
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
  outline-offset:2px;
}
</style>
