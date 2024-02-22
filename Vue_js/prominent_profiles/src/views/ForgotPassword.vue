<template>
  <div class="login-container">
    <h1>Forgot Password</h1>
    <form @submit.prevent="submitEmail">
      <div class="form-group">
        <label class="label" for="email">Email:</label>
        <input class="input-field" type="email" id="email" v-model="email" required autofocus />
        <button class="login-button" type="submit" :disabled="isSubmitting">Submit</button>
        <p class="validation-message" v-if="message">{{ message }}</p>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config'
import VueCookies from 'vue-cookie'

export default {
  name: 'ForgotPasswordPage',
  setup () {
    const email = ref('')
    const isSubmitting = ref(false)
    const message = ref('')

    const submitEmail = async () => {
      isSubmitting.value = true
      message.value = ''

      try {
        const csrfToken = VueCookies.get('csrftoken')
        await axios.post(`${API_BASE_URL}/accounts/api/password_reset/`, { email: email.value }, {
          headers: {
            'X-CSRFToken': csrfToken
          }
        })
        message.value = 'If a Prominent Profiles account with that email exists, we have sent a password reset link.'
      } catch (error) {
        console.error('Password reset error:', error)
        message.value = 'An error occurred. Please try again later.'
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      email,
      isSubmitting,
      message,
      submitEmail
    }
  }
}
</script>

<style scoped>

.form-group {
  margin-bottom: 20px;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
