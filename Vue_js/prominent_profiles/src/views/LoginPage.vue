<template>
  <div class="login-container">
    <h1 class="page-title">Hi!</h1>
    <h2 class="page-title">Prominent Profiles is Better When You Login</h2>

    <div class="form-group">
      <p v-if="loginErrorMessage" class="validation-message">{{ loginErrorMessage }}</p>
      <label for="emailPhone" class="label">Email / Phone:</label>
      <input type="text"
             id="emailPhone"
             ref="emailPhoneInput"
             v-model="emailPhone"
             class="input-field"
             @keyup.enter="focusPasswordInput"/>
    <p v-if="validationMessageUser" class="validation-message">{{ validationMessageUser }}</p>
    </div>

    <div class="form-group">
      <label for="password" class="label">Password:</label>
      <input type="password"
             id="password"
             ref="passwordInput"
             v-model="password"
             class="input-field"
             @keyup.enter="login"/>
    <p v-if="validationMessagePassword" class="validation-message">{{ validationMessagePassword }}</p>
  </div>
    <div class="button-group">
      <button class="login-button signup-button"
              @click="signUp" >Sign Up</button>
      <button class="login-button"
              @click="login" >Login</button>
    </div>
  </div>
</template>
<script>
import { ref, watch } from 'vue'
import VueCookies from 'vue-cookie'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginPage',

  setup () {
    const emailPhone = ref('')
    const password = ref('')
    const validationMessageUser = ref('')
    const validationMessagePassword = ref('')
    const router = useRouter()
    const loginErrorMessage = ref('')

    let validationTimerUser = null
    let validationTimerPassword = null

    const focusPasswordInput = () => {
      document.getElementById('password').focus()
    }

    const login = () => {
      if (validationMessageUser.value === '' && validationMessagePassword.value === '') {
        axios
          .post(`${API_BASE_URL}/accounts/api/token/`, {
            email: emailPhone.value,
            password: password.value
          })
          .then((response) => {
            VueCookies.set('access_token', response.data.access, { expires: '15m' })
            VueCookies.set('refresh_token', response.data.refresh, { expires: '7d' })
            // Redirect to the dashboard
            router.push('/dashboard')
            loginErrorMessage.value = ''
            console.log(VueCookies.get('access_token'))
            console.log(VueCookies.get('refresh_token'))
          })
          .catch((error) => {
            if (error.response && error.response.data && error.response.data.detail) {
              loginErrorMessage.value = error.response.data.detail // Set custom error message
            } else {
              loginErrorMessage.value = 'An unexpected error occurred. Please try again later.'
            }
          })
      } else {
        console.log('Login cannot proceed with improper input.')
      }
    }

    const signUp = () => {
      router.push('/sign-up')
    }

    const validateUserNameInput = () => {
      // Clear the previous timer
      clearTimeout(validationTimerUser)

      // Set a new timer to wait for 500 milliseconds (adjust as needed)
      validationTimerUser = setTimeout(() => {
        if (emailPhone.value !== '') {
          // Validation criteria
          const isPhoneNumber = /^\d{1,16}$/.test(emailPhone.value)
          const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailPhone.value)

          // Validation message updated based on email/phone input
          if (!(isPhoneNumber || isEmail)) {
            validationMessageUser.value = 'Invalid email or phone number format'
          } else {
            validationMessageUser.value = ''
          }
        } else {
          validationMessageUser.value = ''
        }
      }, 1000)
    }

    const validatePassword = () => {
      clearTimeout(validationTimerPassword)

      validationTimerPassword = setTimeout(() => {
        if (password.value !== '') {
          const isStrongPassword = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(password.value)

          validationMessagePassword.value = ''

          // Validation message updated based on password input
          if (!isStrongPassword) {
            validationMessagePassword.value = 'Password must be at least 8 characters long and contain at least one letter and one number.'
          }
        } else {
          validationMessagePassword.value = ''
        }
      }, 1000)
    }

    // Watch for changes in emailPhone and password and trigger validation
    watch(emailPhone, validateUserNameInput)
    watch(password, validatePassword)

    return {
      emailPhone,
      password,
      validationMessageUser,
      validationMessagePassword,
      focusPasswordInput,
      loginErrorMessage,
      login,
      signUp
    }
  }
}

</script>
<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 12vh;
  height: 60vh;
}

.page-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column; /* Keeping inputs in line and aesthetic */
  align-items: center;
  margin-bottom: 15px;
}

.label {
  margin-bottom: 5px;
  font-size: large;
}

.input-field {
  width: 20vw;
  min-width: 300px;
  font-size: large;
  height: 40px;
  text-align: left;
  font-weight: bold;
  text-decoration: none;
  background-color: rgba(117, 91, 180, 0.65);
  color: #fff;
  border: none;
  padding: 5px;
  border-radius: 5px;
}

.login-button {
  cursor: pointer;
  height: 35px;
  width: 120px;
  padding-left: 10px;
  padding-right: 10px;
  background-color: #755BB4;
  border-radius: 5px;
  margin-top: 10px;
  margin-left: 20px;
  margin-right: 20px;
  background-color: rgba(117, 91, 180, 0.65);
  font-weight: bold;
  font-size: 1.2rem;
  color: ghostwhite;
  text-decoration: none;
  transition: color 0.3s ease;
  border-radius: 5px;
}

.login-button:hover {
  outline: 2px solid #fff;
  outline-offset: 10px;
}

.button-group {
  display: flex;
  flex-direction: row;
}

.validation-message {
  /* Very light red background for better visibility */
  color: #f44336;
  background-color: #ffebee;
  border: 1px solid #f44336;
  padding: 10px;
  margin-top: 10px;
  border-radius: 5px;
  width: 20vw;
  text-align: center;
}

</style>
