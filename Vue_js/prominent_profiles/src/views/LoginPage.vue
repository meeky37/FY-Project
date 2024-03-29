<template>
  <div class="login-container">
    <h1 class="page-title">Hi!</h1>
    <h2 class="page-title">Prominent Profiles is Better When You Login</h2>

    <div class="form-group">
      <p v-if="loginErrorMessage" class="validation-message">{{ loginErrorMessage }}</p>
      <button class="wide-button"
              @click="forgotPassword"
              v-if="loginErrorMessage"
              >Forgot Password?</button>
      <label for="emailPhone" class="label">Email/Phone:</label>
      <input type="text"
             id="emailPhone"
             ref="emailPhoneInput"
             v-model="emailPhone"
             class="input-field"
             @keyup.enter="focusPasswordInput"/>
    <p v-if="displayEmailPhoneMessage" class="validation-message">{{ validationMessageEmailPhone }}</p>
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
      <button class="login-button"
              @click="signUp" >Sign Up</button>
      <button class="login-button"
              @click="login" >Login</button>
    </div>
  </div>
</template>
<script>
import { computed, ref } from 'vue'
import VueCookies from 'vue-cookie'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'
import { useRouter } from 'vue-router'
import {
  useEmailValidation,
  usePasswordValidation, usePhoneValidation
  // usePhoneValidation
} from '@/shared_methods/validationUtils'

export default {
  name: 'LoginPage',

  setup () {
    const emailPhone = ref('')
    const password = ref('')
    const validationMessageUser = ref('')
    const router = useRouter()
    const loginErrorMessage = ref('')
    const { validationMessagePassword } = usePasswordValidation(password)
    const { validationMessagePhone } = usePhoneValidation(emailPhone)
    const { validationMessageEmail } = useEmailValidation(emailPhone)

    const displayEmailPhoneMessage = computed(() => {
      return validationMessageEmail.value !== '' && validationMessagePhone.value !== ''
    })

    const isEmailInput = computed(() => emailPhone.value.includes('@'))

    const validationMessageEmailPhone = computed(() => {
      if (isEmailInput.value) {
        return validationMessageEmail.value
      } else {
        return validationMessagePhone.value
      }
    })

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
              console.log(error)
              loginErrorMessage.value = 'An unexpected error occurred. Please try again later.'
            }
          })
      } else {
        console.log('Login cannot proceed with improper input.')
      }
    }

    const showForgotPassword = computed(() => {
      return loginErrorMessage.value === 'No active account found with the given credentials'
    })

    const signUp = () => {
      router.push('/sign-up')
    }

    const forgotPassword = () => {
      router.push('/forgot-password')
    }
    // const validateUserNameInput = () => {
    //   // Clear the previous timer
    //   clearTimeout(validationTimerUser)
    //
    //   // Using a new timer
    //   // to wait for 1000 milliseconds so user gets a chance to input without pop up
    //   validationTimerUser = setTimeout(() => {
    //     if (emailPhone.value !== '') {
    //       // Validation message updated based on email/phone input
    //       // if (validationMessageEmail.value === '' &&
    //       //     validationMessagePhone.value === '') {
    //       if (validationMessageEmail.value === '') {
    //         validationMessageUser.value = 'Invalid email/phone format (use +44)'
    //       } else {
    //         validationMessageUser.value = ''
    //       }
    //     } else {
    //       validationMessageUser.value = ''
    //     }
    //   }, 1000)
    // }

    // Watch for changes in emailPhone and password and trigger validation
    // watch(emailPhone, validateUserNameInput)

    return {
      emailPhone,
      password,
      validationMessageEmailPhone,
      validationMessagePassword,
      displayEmailPhoneMessage,
      focusPasswordInput,
      loginErrorMessage,
      login,
      signUp,
      forgotPassword,
      showForgotPassword
    }
  }
}

</script>

<style>
/* Deliberately not scoped to apply to ResetPassword, ForgotPassword pages */
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

.wide-button {
  cursor: pointer;
  height: 35px;
  width: 250px;
  padding-left: 10px;
  padding-right: 10px;
  background-color: #755BB4;
  border-radius: 5px;
  margin: 10px 20px 20px;
  background-color: rgba(117, 91, 180, 0.65);
  font-weight: bold;
  font-size: 1.2rem;
  color: ghostwhite;
  text-decoration: none;
  transition: color 0.3s ease;
  border-radius: 5px;
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
  margin-top: 20px;
  border-radius: 5px;
  width: 20vw;
  min-width: 300px;
  text-align: center;
}

</style>
