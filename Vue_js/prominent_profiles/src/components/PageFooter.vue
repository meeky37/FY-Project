<template>
  <footer>
<!--    <p>&copy; Prominent Profiles {{ currentYear }}</p>-->
    <p>Prominent Profiles {{ currentYear }}</p>
  </footer>
</template>

<script>
export default {
  data () {
    return {
      // Auto update footer date with current YYYY
      currentYear: new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
footer {
  text-align: center;
  background-color: white;
  position: relative;
  bottom: 0;
  width: 100%;
  height: fit-content;
}
</style>
