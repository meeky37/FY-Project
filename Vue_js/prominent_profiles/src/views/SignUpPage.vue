<template>
<div>
  <h1 class="page-title">Let's Create Your Account</h1>

  <div class="register-container">
     <div class="form-group">
      <label for="firstName" class="label">First Name:</label>
      <input type="text"
             id="firstName"
             ref="firstNameInput"
             v-model="firstName"
             class="input-field"
             @keyup.enter="focusLastNameInput"/>
      <p v-if="validationMessageFirstName" class="validation-message">{{ validationMessageFirstName }}</p>
    </div>

    <div class="form-group">
      <label for="lastName" class="label">Last Name:</label>
      <input type="text"
             id="lastName"
             ref="lastNameInput"
             v-model="lastName"
             class="input-field"
             @keyup.enter="focusEmailInput"/>
      <p v-if="validationMessageLastName" class="validation-message">{{ validationMessageLastName }}</p>
    </div>

    <div class="form-group">
      <label for="email" class="label">Email:</label>
      <input type="text"
             id="email"
             ref="emailInput"
             v-model="email"
             class="input-field"
             @keyup.enter="focusLocationInput"/>
      <p v-if="validationMessageEmail" class="validation-message">{{ validationMessageEmail }}</p>
    </div>

    <div class="form-group">
      <label for="location" class="label">Location:</label>
      <select id="location" v-model="location" class="dropdown">
        <option value="" selected>Select a location</option>
        <option v-for="country in sortedCountries" :key="country.code" :value="country.name">
          {{ country.name }}
        </option>
      </select>
    </div>

    <div class="form-group" v-if="location === 'United Kingdom'">
      <label for="phone" class="label">Mobile Number:</label>
      <input type="text"
         id="phone"
         ref="phoneInput"
         v-model="phone"
         class="input-field"
         :disabled="location !== 'United Kingdom'"
         placeholder="Mobile number"
        @keyup.enter="focusDOBInput"/>
      <p v-if="validationMessagePhone" class="validation-message">{{ validationMessagePhone }}</p>
    </div>

    <div class="form-group">
    <label for="dob" class="label">Date of Birth:</label>
    <VDatePicker v-model="dateOfBirth"
                 :color="selectedColor"
                 :disabled-dates="disabledDates"
                  id="dob"/>
  </div>
</div>

    <div class="form-group">
      <label for="password" class="label">Password:</label>
      <input type="password"
             id="password"
             ref="passwordInput"
             v-model="password"
             class="input-field"
             @keyup.enter="focusConfirmPasswordInput"/>
      <p v-if="validationMessagePassword" class="validation-message">{{ validationMessagePassword }}</p>
    </div>

      <div class="form-group">
    <label for="confirmPassword" class="label">Confirm Password:</label>
    <input type="password"
           id="confirmPassword"
           ref="confirmPasswordInput"
           v-model="confirmPassword"
           class="input-field"
           @keyup.enter="register"/>
    <p v-if="validationMessageConfirmPassword" class="validation-message">{{ validationMessageConfirmPassword }}</p>
  </div>

      <div class="form-group">
        <p>By signing up, you agree to our <router-link to="/privacypolicy">Privacy Policy</router-link>.</p>
      </div>

      <div class="form-group">
        <label for="privacyPolicyCheckbox" class="label">
          <input type="checkbox" id="privacyPolicyCheckbox" v-model="privacyPolicyConfirmed">
          I have read and understood the Privacy Policy
        </label>
      </div>

    <div class="button-group">
      <button class="login-button signup-button"
              @click="register" >Sign Up</button>
    </div>
  <p v-if="signUpMessage">{{ signUpMessage }}</p>
  </div>
</template>

<script>
import { computed, onActivated, ref, watch } from 'vue'
// import VueCookies from 'vue-cookie'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'
import { useRouter } from 'vue-router'
import { countries } from 'countries-list'

import {
  useEmailValidation, useFirstNameValidation, useLastNameValidation,
  usePhoneValidation, usePasswordValidation, useConfirmPasswordValidation
} from
  '@/shared_methods/validationUtils'

export default {
  name: 'RegisterPage',
  setup () {
    const router = useRouter()
    const email = ref('')
    const phone = ref('')
    const firstName = ref('')
    const lastName = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const location = ref('')
    const dateOfBirth = ref(null)
    const privacyPolicyConfirmed = ref(false)

    const { validationMessageEmail } = useEmailValidation(email)
    const { validationMessageFirstName } = useFirstNameValidation(firstName)
    const { validationMessageLastName } = useLastNameValidation(lastName)
    const { validationMessagePhone } = usePhoneValidation(phone)
    const { validationMessagePassword } = usePasswordValidation(password)
    const { validationMessageConfirmPassword } = useConfirmPasswordValidation(password, confirmPassword)

    const signUpMessage = ref('')
    const selectedColor = ref('teal')
    const currentDate = new Date()
    // 16 Years Minimum Age (GDPR)
    const disabledDates = ref([{
      start: new Date(currentDate.getFullYear() - 16,
        currentDate.getMonth(), currentDate.getDate())
    }])

    onActivated(async () => {
    // When component is activated clear the password field from any previous use
      password.value = ''
      confirmPassword.value = ''
    })

    const focusPhoneInput = () => {
      document.getElementById('phone').focus()
    }

    const focusDOBInput = () => {
      document.getElementById('dob').focus()
    }

    const focusLocationInput = () => {
      document.getElementById('location').focus()
    }

    const focusEmailInput = () => {
      document.getElementById('email').focus()
    }

    const focusLastNameInput = () => {
      document.getElementById('lastName').focus()
    }

    const focusPasswordInput = () => {
      document.getElementById('password').focus()
    }
    const focusConfirmPasswordInput = () => {
      document.getElementById('confirmPassword').focus()
    }

    const register = () => {
      if (
        privacyPolicyConfirmed.value &&
        validationMessageEmail.value === '' &&
        validationMessagePhone.value === '' &&
        validationMessageFirstName.value === '' &&
        validationMessageLastName.value === '' &&
        validationMessagePassword.value === '' &&
        validationMessageConfirmPassword.value === '' &&
        email.value !== null &&
        phone.value !== null &&
        dateOfBirth.value !== null &&
        location.value !== '' &&
        firstName.value !== null &&
        lastName.value !== null &&
        password.value !== null &&
        password.value === confirmPassword.value
      ) {
        axios
          .post(`${API_BASE_URL}/accounts/api/register/`, {
            email: email.value,
            phone_number: phone.value,
            date_of_birth: dateOfBirth.value.toISOString().slice(0, 10),
            location: location.value,
            first_name: firstName.value,
            last_name: lastName.value,
            password: password.value
          })
          .then((response) => {
            // Successful reg outcome
            console.log('Registration successful:', response)

            // Clearing form
            firstName.value = ''
            lastName.value = ''
            email.value = ''
            phone.value = ''
            dateOfBirth.value = null
            location.value = ''
            password.value = ''
            confirmPassword.value = ''
            // Redirect to the login page
            router.push('/login')
          })
          .catch((error) => {
            console.error('Registration error:', error)
            // Display custom error message for duplicate email
            if (error.response && error.response.data.errors &&
                error.response.data.errors.email === 'This email is already registered.') {
              signUpMessage.value = error.response.data.errors.email
            } else if (error.response && error.response.data.errors &&
                error.response.data.errors.phone === 'This mobile number is already registered.') {
              signUpMessage.value = error.response.data.errors.phone
            } else {
              signUpMessage.value = 'An error occurred during registration.'
            }
          })
      } else {
        console.log('Registration cannot proceed with improper input.')
        signUpMessage.value = 'Please check ALL your inputs are valid'
      }
    }

    const sortedCountries = computed(() => {
      // Create a copy of the countries array
      const countriesCopy = [...Object.values(countries)]

      // Sort countries alphabetically
      countriesCopy.sort((a, b) => a.name.localeCompare(b.name))

      // 'United Kingdom' to the beginning of the array for convenience
      const ukIndex = countriesCopy.findIndex(country => country.name === 'United Kingdom')
      if (ukIndex !== -1) {
        const ukCountry = countriesCopy.splice(ukIndex, 1)[0]
        countriesCopy.unshift(ukCountry)
      }

      return countriesCopy
    })

    // Watch for changes in input fields and trigger validation
    // I have moved this into validationUtils.js
    watch(location, (newVal) => {
      if (newVal === 'United Kingdom' && !phone.value.startsWith('+44')) {
        phone.value = '+44' + phone.value
      }
    })
    return {
      firstName,
      lastName,
      email,
      phone,
      dateOfBirth,
      selectedColor,
      location,
      sortedCountries,
      disabledDates,
      password,
      confirmPassword,
      privacyPolicyConfirmed,
      validationMessageFirstName,
      validationMessageLastName,
      validationMessageEmail,
      validationMessagePhone,
      validationMessagePassword,
      validationMessageConfirmPassword,
      signUpMessage,
      focusPhoneInput,
      focusDOBInput,
      focusLocationInput,
      focusEmailInput,
      focusLastNameInput,
      focusPasswordInput,
      focusConfirmPasswordInput,
      register
    }
  }
}

</script>

<style scoped>
.register-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: auto;
  margin-top: 20px;
}

.page-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 15px;
}

.label {
  margin-bottom: 5px;
  font-size: large;
}

.login-button {
  cursor: pointer;
  height: 35px;
  width: 120px;
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

.login-button:hover {
  outline: 2px solid #fff;
  outline-offset: 10px;
}

.button-group {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.dropdown {
  font-size: large;
  height: 45px;
  text-align: left;
  font-weight: bold;
  text-decoration: none;
  background-color: rgba(117, 91, 180, 0.65);
  color: #fff;
  border: none;
  border-radius: 5px;
  min-width: 300px;
  width: 20.5vw;
}

.input-field {
  font-size: large;
  height: 40px;
  min-width: 300px;
  text-align: left;
  font-weight: bold;
  text-decoration: none;
  background-color: rgba(117, 91, 180, 0.65);
  color: #fff;
  border: none;
  padding: 5px;
  border-radius: 5px;
  width: 20vw;
}

</style>
