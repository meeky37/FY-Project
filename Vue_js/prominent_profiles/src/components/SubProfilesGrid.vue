<template>
  <div class="card">
        <div class="grid-container">
    <SubProfileCard v-for="(entry) in entities" :key="entry" :entry="entry" />
  </div>
     </div>
</template>

<script setup>
import SubProfileCard from './SubProfileCard.vue'
import { API_BASE_URL } from '@/config'
import axios from 'axios'
import { ref, onMounted, onActivated, watch } from 'vue'
import { useRoute } from 'vue-router'
import VueCookies from 'vue-cookie'

const entities = ref([])
const route = useRoute()
const fetchData = async () => {
  // Making API call conditional on access token as dashboard may be briefly visited before
  // redirect when logged out.
  const accessToken = VueCookies.get('access_token')
  if (accessToken) {
    try {
      const csrfToken = VueCookies.get('csrftoken')
      const response = await axios.get(`${API_BASE_URL}/accounts/api/get_sub_list/`, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        withCredentials: true
      })

      console.log(response)
      entities.value = response.data.subscribed_entities.map((item) => ({
        entity_id: item.id,
        entity_name: item.name
      }))
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }
}

onMounted(() => {
  console.log('Component is mounted')
  fetchData()
})

watch(() => route.query, async () => {
  // We update sub profiles grid when URL changes
  // (as user may have just unsubscribed and returned to dashboard)
  console.log('Route query changed!')
  await fetchData()
}, { deep: true })

onActivated(() => {
  console.log('Component is activated')
  fetchData()
})
</script>

<style scoped>
  .card {
    position: relative;
    overflow: hidden;
    margin: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    min-height: 20vh;
    width: auto;
  }

  img {
    width: 100%;
    height: auto;
    max-height: 100%;
    object-fit: cover;
  }

  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(348px, 1fr));
    column-gap: 2px;
    row-gap: 2px;
  }
</style>
