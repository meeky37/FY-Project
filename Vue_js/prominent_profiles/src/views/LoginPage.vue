<template>
  <div class="login-container">
    <h1 class="page-title">Hi!</h1>
    <h2 class="page-title">Prominent Profiles is Better When You Login</h2>

    <div class="form-group">
      <label for="emailPhone" class="label">Email / Phone:</label>
      <input type="text" id="emailPhone" v-model="emailPhone" class="input-field" />
    </div>

    <div class="form-group">
      <label for="password" class="label">Password:</label>
      <input type="password" id="password" v-model="password" class="input-field" />
    </div>

    <div class="button-group">
      <button @click="signup" class="login-button signup-button">Sign Up</button>
      <button @click="login" class="login-button">Login</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',

  data () {
    return {
      emailPhone: '',
      password: ''
    }
  },

  methods: {
    SignUp () {
      console.log('Sign Up To Come Later')
    },

    login () {
      console.log('Login To Come Later')
      this.$router.push('/dashboard')
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
</style>
