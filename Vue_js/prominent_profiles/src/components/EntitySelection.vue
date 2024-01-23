<template>
  <div>
    <div class="entity-selection-container">
      <label for="entityDropdown" class="label"></label>
      <div class="dropdown-container">
        <select id="entityDropdown" v-model="selectedEntity" class="dropdown">
          <option value="" selected>Select A Profile</option>
          <option v-for="entity in entities" :key="entity.id" :value="entity.id">
            {{ entity.name }}
          </option>
        </select>
        <div class="action-container">
      <div class="button-container" @click="selectRandomEntity">
        <font-awesome-icon :icon="['fas', 'shuffle']" style="color: #ffffff;" />
      </div>
      </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
</script>

<script>
import { API_BASE_URL } from '@/config.js'

export default {
  name: 'EntitySelection',

  data () {
    return {
      entities: [],
      selectedEntity: ''
    }
  },

  created () {
    // Fetch the list of entities with app_visible=true
    this.fetchVisibleEntities()
  },

  watch: {
    // Replacement for button use - ugly.
    selectedEntity (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.redirectToEntityPage()
        this.selectedEntity = ''
      }
    }
  },

  methods: {
    fetchVisibleEntities () {
      const apiUrl = `${API_BASE_URL}/profiles_app/entities/`

      fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
          this.entities = data

          // Check if a default entity is pre-selected (from the URL)
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
    },
    selectRandomEntity () {
      if (this.entities.length > 0) {
        // Generate a random index to pick entity
        const randomIndex = Math.floor(Math.random() * this.entities.length)
        this.selectedEntity = this.entities[randomIndex].id
        this.redirectToEntityPage()
      } else {
        console.log('No entities available for random selection.')
      }
    }
  }
}
</script>

<style scoped>
.entity-selection-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0px;
}

.label {
  margin-right: 10px;
  font-size: large;
}

.dropdown-container {
  display: flex;
  align-items: center;
}

.dropdown {
  width: 20vw;
  font-size: large;
  height: 40px;
  margin-right: 10px;
  margin-left: 30px;
  text-align: left;
  font-weight: bold;
  text-decoration: none;
}

.button-container {
  cursor: pointer;
  font-size: 16px;
  height: 35px;
  display: flex;
  align-items: center;
  padding-left: 10px;
  padding-right: 10px;
  background-color: #755BB4;
  border-radius: 5px;
  margin-left: 20px; /* Space between dropdown and button */
  margin-right: 60px;
}

.button-container:hover {
   outline: 2px solid #fff;
   outline-offset: 3px;
}
</style>
