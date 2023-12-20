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
      <!-- Box for Article Photo -->
      <div class="article-box">
        <h2>Article Photo</h2>
        <div class="article-photo">
          <img
            :src="Article[0].image_url"
            alt="Article Photo"
          />
        </div>
      </div>

      <!-- Box for Entity Spotlight -->
      <div class="entity-box">
        <h2>Entity Spotlight</h2>
        <div>
          <p v-if="bingEntity[0] && bingEntity[0].name">Name: {{ bingEntity[0].name }}</p>
          <div v-if="bingEntity[0].image_url" class="entity-photo">
            <img
              :src="bingEntity[0].image_url"
              alt="Entity Photo"
            />
            <p v-if="bingEntity[0] && bingEntity[0].display_hint">{{bingEntity[0].display_hint
              }}</p>
              <div class="chart-container">
              <Doughnut :data="chartdata" :options="options" />
            </div>
          </div>
        </div>
      </div>
      </div>

    <PageFooter/>
  </div>
</template>

<script>
import PageFooter from '../components/PageFooter.vue'
import { API_BASE_URL } from '@/config.js'
import 'chart.js/auto'
import { Doughnut } from 'vue-chartjs'

export default {
  name: 'ArticlePage',

  components: {
    PageFooter,
    Doughnut
  },
  data () {
    return {
      Article: [],
      bingEntity: [],
      isLoading: false,
      chartdata: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            label: 'Sentiment Analysis',
            backgroundColor: ['mediumseagreen', 'deepskyblue', 'indianred'],
            data: [10, 60, 30]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '50%'
      }
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
      // Dynamically select the parameter to watch.
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
          // const index = this.bingEntity.findIndex((item) => item.id === data.id)

          if (id !== this.$route.params.entityId) {
            // If ID doesn't match route parameter, then I append the new data.
            this.bingEntity.push(data)
          } else {
            // Otherwise, I replace the first element with the new data
            this.bingEntity.unshift(data)
          }
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
    justify-content: space-around;
    margin-top: 20px;
  }

  .article-box,
  .entity-box {
    border: 1px solid #ccc;
    min-width: 20vw;
    max-width: 50vw;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }

  .article-photo img{
    max-width: 100%;
    height: 30vh;
    border-radius: 8px;
  }

.entity-photo img{
  max-width: 100%;
    height: 15vh;
    border-radius: 8px;
}
</style>
