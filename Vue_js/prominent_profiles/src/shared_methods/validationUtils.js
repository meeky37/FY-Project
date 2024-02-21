import { ref, watch } from 'vue'
import validator from 'validator'

export function useEmailValidation (email) {
  const validationMessageEmail = ref('')
  let validationTimerEmail = null

  const validateEmail = (email) => {
    clearTimeout(validationTimerEmail)
    validationTimerEmail = setTimeout(() => {
      if (email !== '') {
        const isEmail = validator.isEmail(email)
        validationMessageEmail.value = isEmail ? '' : 'Invalid email format'
      } else {
        validationMessageEmail.value = ''
      }
    }, 1000)
  }
  watch(email, validateEmail)
  return { validationMessageEmail, validateEmail }
}

export function useFirstNameValidation (firstName) {
  const validationMessageFirstName = ref('')
  let validationTimerFirstName = null

  const validateFirstName = (firstName) => {
    clearTimeout(validationTimerFirstName)
    validationTimerFirstName = setTimeout(() => {
      if (!/^[a-zA-Z]*$/.test(firstName)) {
        validationMessageFirstName.value = 'Only letters permitted in first name entry'
      } else if (firstName.length < 2) {
        validationMessageFirstName.value = 'First name must be at least 2 characters long'
      } else {
        validationMessageFirstName.value = ''
      }
    }, 1000)
  }
  watch(firstName, validateFirstName)
  return { validationMessageFirstName, validateFirstName }
}

export function useLastNameValidation (lastName) {
  const validationMessageLastName = ref('')
  let validationTimerLastName = null

  const validateLastName = (lastName) => {
    clearTimeout(validationTimerLastName)
    validationTimerLastName = setTimeout(() => {
      if (!/^[a-zA-Z]*$/.test(lastName)) {
        validationMessageLastName.value = 'Only letters permitted in last name entry'
      } else if (lastName.length < 2) {
        validationMessageLastName.value = 'Last name must be at least 2 characters long'
      } else {
        validationMessageLastName.value = ''
      }
    }, 1000)
  }
  watch(lastName, validateLastName)
  return { validationMessageLastName, validateLastName }
}

export function usePhoneValidation (phone) {
  const validationMessagePhone = ref('')
  let validationTimerPhone = null

  const validatePhone = () => {
    clearTimeout(validationTimerPhone)
    validationTimerPhone = setTimeout(() => {
      const trimmedPhone = phone.value
      if (trimmedPhone.startsWith('+44') && trimmedPhone.length > 3) {
        const nationalFormatPhone = '0' + trimmedPhone.substring(3)
        const isPhoneNumber = validator.isMobilePhone(nationalFormatPhone, 'en-GB')
        validationMessagePhone.value = isPhoneNumber ? '' : 'Invalid UK mobile number format'
      } else if (!trimmedPhone.startsWith('+44')) {
        validationMessagePhone.value = '+44 is required at start here'
      } else {
        validationMessagePhone.value = ''
      }
    }, 1000)
  }
  watch(phone, validatePhone)
  return { validationMessagePhone, validatePhone }
}

export function usePasswordValidation (password) {
  const validationMessagePassword = ref('')
  let validationTimerPassword = null

  const validatePassword = () => {
    clearTimeout(validationTimerPassword)
    validationTimerPassword = setTimeout(() => {
      const isStrongPassword = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(password.value)
      validationMessagePassword.value =
      isStrongPassword ? '' : 'Password must be at least 8 characters long and contain at least one letter and one number.'
    }, 1000)
  }
  watch(password, validatePassword)
  return { validationMessagePassword, validatePassword }
}

export function useConfirmPasswordValidation (password, confirmPassword) {
  const validationMessageConfirmPassword = ref('')
  let validationTimerConfirmPassword = null

  const validateConfirmPassword = () => {
    clearTimeout(validationTimerConfirmPassword)
    validationTimerConfirmPassword = setTimeout(() => {
      validationMessageConfirmPassword.value = password.value === confirmPassword.value ? '' : 'Passwords do not match'
    }, 1000)
  }
  watch([password, confirmPassword], validateConfirmPassword)
  return { validationMessageConfirmPassword, validateConfirmPassword }
}
