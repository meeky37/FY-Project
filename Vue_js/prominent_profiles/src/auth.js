import axios from 'axios'
import VueCookies from 'vue-cookie'
import { API_BASE_URL } from '@/config.js'

// Used in multiple components so appropriate to move here
export const checkAuthenticationCommon = async () => {
  const accessToken = VueCookies.get('access_token')

  if (!accessToken) {
    // Attempt to refresh the access token using the refresh token
    const refreshToken = VueCookies.get('refresh_token')
    if (refreshToken) {
      try {
        const response = await axios.post(`${API_BASE_URL}/accounts/api/token/refresh/`, {
          refresh: refreshToken
        })
        // Update the access token cookie
        VueCookies.set('access_token', response.data.access)
        console.log('common check auth returning true')
        return true
      } catch (refreshError) {
        console.error('Token refresh failed', refreshError)
        return false
      }
    }
  }
  console.log(!!accessToken)
  return !!accessToken
}
