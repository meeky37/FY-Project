import axios from 'axios'
import VueCookies from 'vue-cookie'
import { API_BASE_URL } from '@/config.js'
import router from '../router'

// Could roll this out to tidy up axios requests across frontend
// axios.defaults.baseURL = 'http://localhost:8000'

axios.interceptors.request.use(
  (config) => {
    // Check if the access token is present and not expired
    const accessToken = VueCookies.get('access_token')
    if (accessToken) {
      // Add the access token to the Authorization header
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Check if the error is due to an expired access token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Attempt to refresh the access token using the refresh token
      const refreshToken = VueCookies.get('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/accounts/api/token/refresh/`, {
            refresh: refreshToken
          })

          // Updating the access token cookie
          VueCookies.set('access_token', response.data.access)

          // Retry the original request with the new access token
          return axios(originalRequest)
        } catch (refreshError) {
          // If refresh fails, redirect to the login page.
          console.error('Token refresh failed', refreshError)
          await router.push('/login')
        }
      }
    }

    return Promise.reject(error)
  }
)
