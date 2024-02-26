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

let refreshAttempts = 0
const MAX_REFRESH_ATTEMPTS = 3 // max number of refresh attempts to prevent hogging connection

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
      if (refreshAttempts < MAX_REFRESH_ATTEMPTS) {
        const refreshToken = VueCookies.get('refresh_token')
        if (refreshToken) {
          try {
            const response = await axios.post(
              `${API_BASE_URL}/accounts/api/token/refresh/`, {
                refresh: refreshToken
              })

            VueCookies.set('access_token', response.data.access)
            refreshAttempts = 0 // reset the counter on successful refresh
            return axios(originalRequest)
          } catch (refreshError) {
            refreshAttempts += 1 // incrementing counter
            console.error('Token refresh failed', refreshError)
            // If max attempts reached, logout the user
            if (refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
              VueCookies.delete('access_token')
              VueCookies.delete('refresh_token')
              await router.push('/login')
            }
          }
        }
      } else {
        // Directly logout the user if max attempts have already been reached without trying to refresh
        VueCookies.delete('access_token')
        VueCookies.delete('refresh_token')
        await router.push('/login')
      }
    }

    return Promise.reject(error)
  }
)
