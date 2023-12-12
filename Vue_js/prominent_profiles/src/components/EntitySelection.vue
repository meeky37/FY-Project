<template>
  <div>
    <div style="display: flex; align-items: center;">
      <label for="entityDropdown" style="margin-right: 10px; font-size: 16px;"></label>
      <select id="entityDropdown" v-model="selectedEntity" style="width: 200px; font-size: 14px; height: 30px;">
        <option value="" disabled selected>Select an entity</option>
        <option v-for="entity in entities" :key="entity.id" :value="entity.id">
          {{ entity.name }}
        </option>
      </select>

      <!-- Button for redirection -->
      <button @click="redirectToEntityPage" style="margin-left: 10px; font-size: 16px; height: 30px;">
        <span>&#9654;</span> <!-- Unicode character for the right arrow symbol -->
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EntitySelection',

  data () {
    return {
      entities: [],
      selectedEntity: null
    }
  },

  created () {
    // Fetch the list of entities with app_visible=true
    this.fetchVisibleEntities()
  },

  methods: {
    fetchVisibleEntities () {
      const apiUrl = 'http://localhost:8008/profiles_app/entities/'

      fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
          this.entities = data

          // Check if a default entity is pre-selected (for example, from the URL)
          // and redirect immediately
          if (this.selectedEntity) {
            this.$router.push('/entity/' + this.selectedEntity)
          }
        })
        .catch(error => {
          console.error('Error fetching entities:', error)
        })
    },

    redirectToEntityPage () {
      // Redirect to the URL related to the selected entity
      if (this.selectedEntity) {
        this.$router.push('/entity/' + this.selectedEntity)
      }
    }
  }
}
</script>

<style scoped>
</style>
