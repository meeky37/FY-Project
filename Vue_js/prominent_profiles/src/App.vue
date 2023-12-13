<template>
  <div>
    <nav>
      <router-link to="/">Home</router-link> |

      <router-link to="/vue">Vue</router-link> |
      <router-link to="/about">About</router-link>
    </nav>

    <!-- Use keep-alive to persist the component across route changes -->
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 10px;
  white-space: nowrap;
  overflow: hidden;
}

nav router-link {
  margin-right: 10px;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
