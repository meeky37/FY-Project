<template>
    <div class="button-container" @click="toggleSubscription">
    <font-awesome-icon v-if="isSubscribed" :icon="['fas', 'check']" style="color: white;" />
    <font-awesome-icon v-else :icon="['fas', 'plus']" style="color: white;" />
  </div>
</template>

<script>
import { ref, onBeforeMount, onUpdated } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'
import VueCookie from 'vue-cookie'
import { checkAuthenticationCommon } from '@/auth.js'
import router from '@/router'

export default {
  props: {
    entityId: {
      type: Number,
      required: true
    }
  },
  setup (props) {
    const isSubscribed = ref(false)
    const toggleSubscription = async () => {
      const isAuthenticated = await checkAuthenticationCommon()

      // If not authenticated, redirect to login so user is on track to use functionality soon
      if (!isAuthenticated) {
        await router.push('/login/')
        return
      }
      console.log(props.entityId)
      const csrfToken = VueCookie.get('csrftoken')

      try {
        // API call to the toggle_subscription endpoint
        const response = await axios.post(
          `${API_BASE_URL}/accounts/api/toggle_sub/${props.entityId}/`,
          {},
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
            },
            withCredentials: true
          }
        )

        if (response.status === 200) {
          // Update the subscription status IF the API call was successful
          isSubscribed.value = !isSubscribed.value
        } else {
          console.error('Error toggling subscription. Server returned:', response.status, response.statusText)
        }
      } catch (error) {
        console.error('Error toggling subscription:', error.message)
      }
    }

    const fetchSubscriptionStatus = async () => {
      const isAuthenticated = await checkAuthenticationCommon()

      if (isAuthenticated) {
        try {
          const csrfToken = VueCookie.get('csrftoken')
          const response = await axios.get(
            `${API_BASE_URL}/accounts/api/get_sub_status/${props.entityId}/`,
            {
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
              },
              withCredentials: true
            }
          )

          if (response.status === 200) {
            isSubscribed.value = response.data.status
          } else {
            console.error('Error fetching subscription status. Server returned:', response.status, response.statusText)
          }
        } catch (error) {
          console.error('Error fetching subscription status:', error.message)
        }
      }
    }

    // Trigger fetchSubscriptionStatus when the component is mounted
    onBeforeMount(fetchSubscriptionStatus)
    onUpdated(fetchSubscriptionStatus)
    return {
      isSubscribed,
      toggleSubscription
    }
  }
}
</script>

<style scoped>

.button-container {
  cursor: pointer;
  font-size: 16px;
  height: 30px;
  width: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #755BB4;
  border-radius: 5px;
  margin-left: 20px; /* Putting distance between Entity Name and Subscription Button */
  margin-right: 60px;
}
</style>
