<template>
  <div>
    <h1 v-if="userData">Hi {{ userData.first_name }}!</h1>
    <h2>Welcome to your dashboard</h2>
    <h3>You'll find your profile subscriptions here</h3>
    <p> Each card shows the number of articles added since your last site visit (excluding
      today's)</p>
    <SubProfilesGrid/>
  </div>
</template>

<script setup>
import axios from 'axios'
import { onActivated, onMounted, ref } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { checkAuthenticationCommon } from '@/auth'
import VueCookie from 'vue-cookie'
import SubProfilesGrid from '@/components/SubProfilesGrid.vue'

const fetchData = async () => {
  try {
    await checkAuthenticationCommon()
    const csrfToken = VueCookie.get('csrftoken')
    const response = await axios.get(`${API_BASE_URL}/accounts/api/get_user_data/`, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'include'
    })

    return response.data
  } catch (error) {
    console.error('Error fetching user data:', error)
    return null
  }
}

const userData = ref(null)

onMounted(async () => {
  // Fetch user data when the component is mounted
  userData.value = await fetchData()
})

onActivated(async () => {
  // Fetch user data when the component is activated to prevent old users name sticking around.
  userData.value = await fetchData()
})
</script>
