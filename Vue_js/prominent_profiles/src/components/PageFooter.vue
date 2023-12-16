<template>
  <footer>
    <p>&copy; Prominent Profiles {{ currentYear }}</p>
  </footer>
</template>

<script>
export default {
  data () {
    return {
      currentYear: new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
footer {
  text-align: center;
  padding: 5px;
  background-color: #f1f1f1;
  position: relative;
  bottom: 0;
  width: 100%;
  margin-top:10px;
  margin-bottom:-10px;
}
</style>
