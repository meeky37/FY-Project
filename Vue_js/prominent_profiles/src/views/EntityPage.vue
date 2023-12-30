<template>
  <div>
    <h1>{{ isLoading ? 'Loading...' : (bingEntity ? bingEntity.name : 'Entity Not Found') }}</h1>

    <!-- Display the image and description (centered) -->
    <div v-if="bingEntity && !isLoading" class="content-container">
      <div class="entity-photo">
        <img
          :src="bingEntity.image_url"
          alt="Entity Photo"
          style="width: auto; min-height: 150px;"
          :title="getAttributionMessage(bingEntity)"
        />
         <a class="attribution-link" @click="openSourcePopup">CREDIT</a>
      </div>

      <div class="description-box">
        <p>{{ bingEntity.description }}</p>
        <p class="source-date">
            <a :href="getDescriptionUrl(bingEntity)" target="_blank">Wikipedia</a>
            <br>
            {{ formatDate(bingEntity.date_added) }}
          </p>
      </div>
    </div>

    <div v-if="showSourcePopup" class="source-popup">
      <p>
        Original Image Source:
        <a :href="getMediaUrl(bingEntity)" target="_blank">{{ getMediaUrl(bingEntity) }}</a>
      </p>
      <button @click="closeSourcePopup">Close</button>
    </div>
    <!-- Use ArticleEntriesContainer to display entries -->
    <ArticleEntriesContainer/>
    <PageFooter/>
  </div>
</template>

<script>
import ArticleEntriesContainer from '../components/ArticleEntriesContainer.vue'
import PageFooter from '../components/PageFooter.vue'
import { API_BASE_URL } from '@/config.js'
import VueCookie from 'vue-cookie'
export default {
  name: 'EntityPage',

  components: {
    ArticleEntriesContainer,
    PageFooter
  },

  data () {
    return {
      bingEntity: null,
      isLoading: false,
      showSourcePopup: false
    }
  },
  watch: {
    '$route.params.id': function (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // Check if newId is defined before triggering bing entity
      if (newId !== undefined) {
        this.fetchBingEntity()
      }
    }
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend

    this.fetchBingEntity()
    VueCookie.set('viewedProfiles', [])
  },

  methods: {
    openSourcePopup () {
      this.showSourcePopup = true
    },
    closeSourcePopup () {
      this.showSourcePopup = false
    },

    fetchBingEntity () {
      this.isLoading = true
      // Use the entity ID from the route parameters
      const entityId = this.$route.params.id

      // Fetch BingEntity JSON from Django backend
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/${entityId}/`

      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          this.bingEntity = data
        })
        .catch((error) => {
          console.error('Error fetching BingEntity:', error)
        })
        .finally(() => {
          this.isLoading = false
        })
    },

    getMediaUrl (bingEntity) {
    // Extract description URL from contractual rules
      const mediaContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/MediaAttribution' &&
        rule.targetPropertyName === 'image'
      )

      const mediaUrl = mediaContract ? mediaContract.url : null
      return mediaUrl
    },

    getAttributionMessage (bingEntity) {
      const mediaUrl = this.getMediaUrl(bingEntity)
      return `Attribution: ${mediaUrl}`
    },

    getDescriptionUrl (bingEntity) {
      // Extract description URL from contractual rules
      const descriptionContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
          rule.targetPropertyName === 'description'
      )
      return descriptionContract ? descriptionContract.url : '#'
    },

    getDescriptionSource (bingEntity) {
      // Extract description source text from contractual rules
      const descriptionContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
          rule.targetPropertyName === 'description'
      )
      return descriptionContract ? descriptionContract.text : 'Unknown Source'
    },

    formatDate (dateString) {
      // Format the date string as desired
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      const date = new Date(dateString)
      return date.toLocaleDateString(undefined, options)
    }
  }
}
</script>

<style scoped>

.content-container {
  display: flex;
  align-items: center;
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
  margin: 0px 30px 0px 30px;
  position: relative;
  min-width: 75vw;
}
.description-box p {
  font-size: medium;
  line-height: 1.6;
  color: #333;
}

.source-date {
  font-size: xx-small;
  text-align: right;
  margin-right: 5px;
  margin-bottom: 0px;
  position: absolute;
  bottom: 0;
  right: 0;
}

.source-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.source-popup a {
  color: blue;
  text-decoration: underline;
  margin-left: 5px;
}

.source-popup button {
  margin-top: 10px;
}

.attribution-link{
  font-size: small;
  color: purple;
  text-decoration: underline;
  cursor: pointer;
}

.attribution-link:hover {
  color: purple;
}
</style>
