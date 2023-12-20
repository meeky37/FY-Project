<template>
 <div>
   <h1>Article Profile</h1>
  <h2 v-if="isLoading">
    Loading...
  </h2>
  <h2 v-else-if="Article && Article.length > 0">
    Headline: <span v-html="Article[0].headline"></span>
  </h2>
  <h2 v-else>
    Article Not Found
  </h2>
    <!-- Display the image and description (centered) -->
    <div v-if="Article && Article.length > 0 && Article[0] && Article[0].image_url" class="content-container">
  <div class="article-photo">
    <img
      :src="Article[0].image_url"
      alt="Article Photo"
      style="width: auto; min-height: 200px;"
    />
  </div>
  <div>
    <p v-if="bingEntity && bingEntity.name">{{ bingEntity.name }}</p>
     <div v-if="bingEntity.image_url" class="entity-photo">
    <img
      :src="bingEntity.image_url"
      alt="Entity Photo"
      style="width: auto; min-height: 200px;"
    />
       </div>
  </div>
</div>
  <div>
  </div>
</div>

    <PageFooter/>
</template>

<script>
import PageFooter from '../components/PageFooter.vue'
import { API_BASE_URL } from '@/config.js'
export default {
  name: 'ArticlePage',

  components: {
    PageFooter
  },

  data () {
    return {
      Article: [],
      bingEntity: null,
      OtherEntities: [],
      isLoading: false
    }
  },

  watch: {
    watchParam (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // Check if newId is defined before triggering bing entity
      if (newId !== undefined) {
        this.isLoading = true
        this.fetchArticleSentiments()
        this.fetchMiniBingEntity()
        this.isLoading = false
      }
    }
  },

  computed: {
    watchParam () {
      // Dynamically select the parameter to watch based on your logic
      return this.$route.params.articleId || this.$route.params.entityId
    }
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend
    this.isLoading = true
    Promise.all([this.fetchArticleSentiments(), this.fetchMiniBingEntity()]).finally(() => {
      this.isLoading = false
    })
  },

  methods: {
    fetchArticleSentiments () {
      // Use the entity ID from the route parameters
      const ArticleId = this.$route.params.articleId
      const EntityId = this.$route.params.entityId

      // Fetch Article JSON from Django backend
      const apiUrl =
        `${API_BASE_URL}/profiles_app/overall_sentiments/exp/article/${EntityId}/${ArticleId}/`
      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          this.Article = data
        })
        .catch((error) => {
          console.error('Error fetching Article info:', error)
        })
    },

    fetchMiniBingEntity (entityId) {
      // Use the entity ID from the route parameters if not provided
      const id = entityId || this.$route.params.entityId

      // Fetch compact BingEntity JSON from Django backend
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/mini/${id}/`

      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          this.bingEntity = data
        })
        .catch((error) => {
          console.error('Error fetching BingEntity:', error)
        })
    }

    // getMediaUrl (bingEntity) {
    // // Extract description URL from contractual rules
    //   const mediaContract = bingEntity.contractual_rules.find(
    //     (rule) => rule._type === 'ContractualRules/MediaAttribution' &&
    //     rule.targetPropertyName === 'image'
    //   )
    //
    //   const mediaUrl = mediaContract ? mediaContract.url : null
    //   return mediaUrl
    // },

    // getAttributionMessage (bingEntity) {
    //   const mediaUrl = this.getMediaUrl(bingEntity)
    //   return `Attribution: ${mediaUrl}`
    // },

    // getDescriptionUrl (bingEntity) {
    //   // Extract description URL from contractual rules
    //   const descriptionContract = bingEntity.contractual_rules.find(
    //     (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
    //       rule.targetPropertyName === 'description'
    //   )
    //   return descriptionContract ? descriptionContract.url : '#'
    // },

    // getDescriptionSource (bingEntity) {
    //   // Extract description source text from contractual rules
    //   const descriptionContract = bingEntity.contractual_rules.find(
    //     (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
    //       rule.targetPropertyName === 'description'
    //   )
    //   return descriptionContract ? descriptionContract.text : 'Unknown Source'
    // },

    // formatDate (dateString) {
    //   // Format the date string as desired
    //   const options = { year: 'numeric', month: 'long', day: 'numeric' }
    //   const date = new Date(dateString)
    //   return date.toLocaleDateString(undefined, options)
    //   }
    // }
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
