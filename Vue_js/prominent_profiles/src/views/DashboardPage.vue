<template>
  <div>
    <h1 v-if="userData">Hi {{ userData.first_name }}!</h1>
    <h2>Welcome to your dashboard</h2>
    <PageFooter />
  </div>
</template>

<script setup>
import axios from 'axios'
import PageFooter from '@/components/PageFooter.vue'
import { onActivated, onMounted, ref } from 'vue'
import { API_BASE_URL } from '@/config.js'

const fetchData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/accounts/api/get_user_data/`)
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

</script>
