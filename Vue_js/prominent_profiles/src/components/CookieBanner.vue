<template>
  <div v-if="!accepted && !nonEssentialRejected" class="cookie-banner">
    <p>This website uses non-essential cookies to aid the determination of trending entities.</p>
    <div class="button-group">
      <button @click="acceptCookies" class="cookie-button accept-button">Accept Cookies</button>
      <button @click="rejectNonEssentialCookies" class="cookie-button reject-button">Reject
        All Non-essential Cookies</button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import VueCookie from 'vue-cookie'

export default {
  setup () {
    const accepted = ref(VueCookie.get('non_essential_cookies_accepted'))
    const nonEssentialRejected = ref(VueCookie.get('non_essential_cookies_rejected'))

    const acceptCookies = () => {
      VueCookie.set('non_essential_cookies_accepted', true)
      accepted.value = true
    }

    const rejectNonEssentialCookies = () => {
      VueCookie.set('non_essential_cookies_rejected', true)
      nonEssentialRejected.value = true
    }

    return {
      accepted,
      nonEssentialRejected,
      acceptCookies,
      rejectNonEssentialCookies
    }
  }
}
</script>

<style scoped>
.cookie-banner {
  background-color: #755BB4;
  color: white;
  padding: 30px;
  border-radius: 5px;
  margin-bottom: 20px;
  margin-top: 10px;
  text-align: center;
}

.button-group {
  display: flex;
  justify-content: center;
}

.cookie-button {
  cursor: pointer;
  height: 35px;
  width: 200px;
  margin: 0 10px;
  font-weight: bold;
  font-size: 1rem;
  border: none;
  border-radius: 5px;
}

.accept-button {
  background-color: #755BB4;
  color: white;
}

.reject-button {
  background-color: #755BB4;
  color: white;
}
</style>
