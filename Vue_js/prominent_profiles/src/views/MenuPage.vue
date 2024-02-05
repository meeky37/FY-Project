<template>
  <div class="menu-container">
    <router-link to="/about" class="menu-item">About</router-link>
    <router-link v-if="!authenticated" to="/login" class="menu-item" @click.prevent="logonRedirect">Login</router-link>
    <router-link v-if="authenticated" to="/dashboard" class="menu-item">Your Dashboard</router-link>
    <button v-if="authenticated" @click="logout" class="menu-item logout-button">Logout</button>
  </div>
</template>

<script>
import { authenticated, logonRedirect, logout } from '../shared_methods/auth_methods.js'

export default {
  setup () {
    return {
      authenticated,
      logonRedirect,
      logout
    }
  }
}
</script>
<style scoped>
.menu-container {
  display: flex;
  flex-direction: column;
  padding: 20px;
  align-items: center;
}

.menu-item, .logout-button {
  background-color: #30d5c8; /* Same green as pp header for consistency :) */
  color: white;
  border: none;
  padding: 15px;
  margin: 10px 0;
  text-decoration: none;
  text-align: center;
  font-size: 18px;
  border-radius: 8px;
  transition: background-color 0.3s, color 0.3s;
  width: 80%;
  box-sizing: border-box;
}

.menu-item:hover, .logout-button:hover {
  background-color: #1e8a8a;
  color: #FFF;
  cursor: pointer;
}

.logout-button {
  background-color: #ff4d4f;
}
</style>
