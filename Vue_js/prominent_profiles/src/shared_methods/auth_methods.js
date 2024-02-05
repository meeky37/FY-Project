import { ref, watch } from 'vue'
import VueCookies from 'vue-cookie'
import router from '@/router'
import axios from 'axios'
import { API_BASE_URL } from '@/config'
import { checkAuthenticationCommon } from '@/auth.js'

export const authenticated = ref(null)

export const checkAuthentication = async () => {
  try {
    authenticated.value = await checkAuthenticationCommon()
  } catch (error) {
    console.error('Error checking authentication:', error)
    await router.push('/login')
  }
}

export const logonRedirect = async () => {
  await checkAuthentication()
  if (authenticated.value) {
    const dashboardRoute = { path: '/dashboard/', query: { key: Date.now() } }
    await router.push(dashboardRoute)
  } else {
    await router.push('/login/')
  }
}

export const logout = async () => {
  VueCookies.delete('access_token')
  VueCookies.delete('refresh_token')

  try {
    const csrfToken = VueCookies.get('csrftoken')
    await axios.post(`${API_BASE_URL}/accounts/logout/`, null, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrfToken }
    })
    authenticated.value = false
    await logonRedirect()
  } catch (error) {
    console.error('Error during logout:', error)
  }
}

watch(() => router.currentRoute.value, async (to) => {
  if (to.path === '/dashboard') {
    await checkAuthentication()
  }
}, { immediate: true })
