<template>
  <div>
    <h1>{{
        isLoading ? 'Loading...' : (Articleheadline ? Articleheadline.name : 'Entity Not Found')
      }}</h1>

    <!-- Display the image and description (centered) -->
    <div v-if="Articleheadline && !isLoading" class="content-container">
      <div class="article-photo">
        <img
          :src="Articleheadline.image_url"
          alt="Article Photo"
          style="width: auto; min-height: 150px;"
          :title="getAttributionMessage(Articleheadline)"
        />
         <a class="attribution-link" @click="openSourcePopup">CREDIT</a>
      </div>

      <div class="description-box">
        <p>{{ Articleheadline.headline }}</p>
        <p class="source-date">
            <a :href="getDescriptionUrl(Articleheadline)" target="_blank">Wikipedia</a>
            <br>
          {{ formatDate(Articleheadline.date_added) }}
        </p>
      </div>
    </div>

    <div v-if="showSourcePopup" class="source-popup">
      <p>
        Original Image Source:
        <a :href="getMediaUrl(Articleheadline)" target="_blank">{{ getMediaUrl(Articleheadline) }}</a>
      </p>
      <button @click="closeSourcePopup">Close</button>
    </div>
    <!-- Use ArticleEntriesContainer to display entries -->
    <PageFooter/>
  </div>
</template>

<script>
import PageFooter from '../components/PageFooter.vue'
import { API_BASE_URL } from '@/config.js'
export default {
  name: 'EntityPage',

  components: {
    PageFooter
  },

  data () {
    return {
      Articleheadline: null,
      isLoading: false,
      showSourcePopup: false
    }
  },
  watch: {
    '$route.params.id': function (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // Check if newId is defined before triggering bing entity
      if (newId !== undefined) {
        this.fetchArticle()
      }
    }
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend
    this.fetchArticle()
  },

  methods: {
    fetchArticle () {
      this.isLoading = true
      // Use the entity ID from the route parameters
      const ArticleId = this.$route.params.id

      // Fetch BingEntity JSON from Django backend
      const apiUrl = `${API_BASE_URL}/profiles_app/${ArticleId}/`

      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          this.Articleheadline = data
        })
        .catch((error) => {
          console.error('Error fetching Article info:', error)
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

.article-photo {
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

</style>
