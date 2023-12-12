<template>
  <div>
     <h1>{{ isLoading ? 'Loading...' : (bingEntity ? bingEntity.name : 'Entity Not Found') }}</h1>

    <!-- Display the image and description (centered) -->
    <div v-if="bingEntity && !isLoading" class="content-container">
      <img :src="bingEntity.image_url" alt="Entity Photo" class="entity-photo">
      <div class="description-box">
        <p>{{ bingEntity.description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EntityPage',

  data () {
    return {
      bingEntity: null,
      isLoading: false
    }
  },

  watch: {
    '$route.params.id': 'fetchBingEntity'
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend
    this.fetchBingEntity()
  },

  methods: {

    fetchBingEntity () {
      this.isLoading = true
      // Use the entity ID from the route parameters
      const entityId = this.$route.params.id

      // Fetch BingEntity JSON from Django backend
      const apiUrl = `http://localhost:8008/profiles_app/bing_entities/${entityId}/`

      fetch(apiUrl)
        .then(response => response.json())
        .then(data => { this.bingEntity = data })
        .catch(error => {
          console.error('Error fetching BingEntity:', error)
        }).finally(() => {
          this.isLoading = false
        })
    }
  }
}
</script>

<style scoped>

.content-container {
  display: flex;
  align-items: center; /* Vertical centering */
}

.entity-photo {
  margin-left: 30px;
  max-width: 300px;
  max-height: 300px;
}

.description-box {
  background-color: #f4f4f4;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin: 5px 30px 30px 30px;
}

.description-box p {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}
</style>
