<template>
  <div class="reset-password-container">
    <h2>Reset Your Password</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label class="label" for="newPassword">New Password:</label>
        <input class="input-field" id="newPassword" type="password" v-model="newPassword" required>
        <p v-if="validationMessagePassword" class="validation-message">{{ validationMessagePassword }}</p>
      </div>

      <div class="form-group">
        <label class="label" for="confirmPassword">Confirm New Password:</label>
        <input class="input-field" id="confirmPassword" type="password" v-model="confirmPassword" required>
        <p v-if="validationMessageConfirmPassword" class="validation-message">{{ validationMessageConfirmPassword }}</p>
      </div>

      <button class="wide-button" type="submit" :disabled="isFormValid.value">
        Reset Password
      </button>
    </form>

    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import {
  useConfirmPasswordValidation,
  usePasswordValidation
} from '@/shared_methods/validationUtils'
import VueCookies from 'vue-cookie'
import { API_BASE_URL } from '@/config'

export default {
  name: 'ResetPassword',
  setup () {
    const route = useRoute()
    const newPassword = ref('')
    const confirmPassword = ref('')
    const isSubmitting = ref(false)
    const message = ref('')
    // Using shared composition API validationUtils methods
    const { validationMessagePassword } = usePasswordValidation(newPassword)
    const { validationMessageConfirmPassword } = useConfirmPasswordValidation(newPassword, confirmPassword)

    const isFormValid = computed(() => {
      return !validationMessagePassword.value && !validationMessageConfirmPassword.value
    })

    const submitForm = async () => {
      if (isFormValid.value) {
        try {
          isSubmitting.value = true
          const { token } = route.query
          const csrfToken = VueCookies.get('csrftoken')

          // We should validate the token first - it may have expired
          const validationResponse = await axios.post(`${API_BASE_URL}/accounts/api/password_reset/validate_token/`, {
            token: token
          }, {
            headers: {
              'X-CSRFToken': csrfToken
            }
          })

          // Check if the token validation was successful
          if (validationResponse.status === 200) {
            // Token is valid, proceed with password reset confirmation
            try {
              await axios.post(`${API_BASE_URL}/accounts/api/password_reset/confirm/`, {
                token: token,
                password: newPassword.value
              }, {
                headers: {
                  'X-CSRFToken': csrfToken
                }
              })
              message.value = 'Your password has been successfully reset. You can now use your new password to log in.'
            } catch (error) {
              console.error('Password reset confirmation error:', error)
              message.value = 'An error occurred while confirming your new password. Please try again.'
            }
          } else {
            // Token validation failed
            message.value = 'This password reset link is invalid or has expired. Please request a new one.'
          }
        } catch (error) {
          console.error('Token validation error:', error)
          message.value = 'This password reset link is invalid or has expired. Please request a new one.'
        } finally {
          isSubmitting.value = false
        }
      }
    }

    // See if works without manual validation
    // validatePassword()
    // validateConfirmPassword()

    return {
      newPassword,
      confirmPassword,
      isSubmitting,
      message,
      submitForm,
      validationMessagePassword,
      validationMessageConfirmPassword,
      isFormValid
    }
  }
}
</script>
