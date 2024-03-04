<template>
  <div v-if="!accepted && !nonEssentialRejected" class="cookie-banner">
    <p>This website uses non-essential cookies to aid the determination of trending entities.</p>
    <p>By using Prominent Profiles, you agree to our <a href="https://www.prominentprofiles.com/privacypolicy" target="_blank" style="color: white;">Privacy Policy</a>.</p>
      <button @click="acceptCookies" class="cookie-button accept-button">Accept Cookies</button>
      <button @click="rejectNonEssentialCookies" class="cookie-button reject-button">Reject
        All Non-essential Cookies</button>
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
  padding: 20px;
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
  height: auto;
  width: auto;
  margin: 0 10px;
  font-weight: bold;
  font-size: 1rem;
  border: none;
  border-radius: 5px;
  margin: 10px;
}

.accept-button {
  background-color: #30d5c8;
  color: white;
  padding: 10px;
}

.reject-button {
  background-color: #30d5c8;
  color: white;
  padding: 10px;
}
</style>
