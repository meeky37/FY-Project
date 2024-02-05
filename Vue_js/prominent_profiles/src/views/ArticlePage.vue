<template>
  <div>
    <h1>Article Analysis</h1>
    <h2 v-if="isLoading">Loading...</h2>
    <h2 v-else-if="Article && Article.length > 0">
      Headline: <span v-html="Article[0].headline"></span>
    </h2>
    <h2 v-else>Article Not Found</h2>

    <!-- Display the image and description (centered) -->
    <div v-if="Article && Article.length > 0 && Article[0]" class="content-container">
      <!-- Box for Article Photo -->
      <div class="article-box">
        <h2> Article Photo</h2>
        <div v-if="Article[0].image_url" class="article-photo">
          <img :src="Article[0].image_url" alt="Article Photo" />
        </div>
        <h2>Published Date</h2>
         <p>{{ formatPublicationDate(Article[0].publication_date) }}</p>
        <h2>Author</h2>
        <p>{{ Article[0].author }}</p>
        <h2>{{getSubsection ( Article[0].url)}}
        <a :href="Article[0].url" target="_blank" rel="noopener noreferrer" class="external-link">
            <font-awesome-icon :icon="['fas', 'external-link-alt']" />
          </a>

        </h2>

      </div>

      <!-- Box for Entity Spotlight -->
      <EntitySpotlight
        :bingEntity="bingEntity"
        :chartdata="chartdata"
        :options="options"
        :re_render="re_render"
        @updateReRender="updateReRender"
        class="flex-box"
      />
      <ArticleOtherEntities
        :Article="otherArticles"
        class="flex-box"
      />
    </div>
  </div>
</template>

<script>
import EntitySpotlight from '@/components/EntitySpotlight.vue'
import { API_BASE_URL } from '@/config.js'
import ArticleOtherEntities from '@/components/ArticleOtherEntities.vue'
import { format } from 'date-fns'
export default {
  name: 'ArticlePage',

  components: {
    ArticleOtherEntities,
    EntitySpotlight
  },
  data () {
    return {
      Article: [],
      bingEntity: [],
      isLoading: false,
      re_render: Boolean,
      chartdata: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            label: 'Sentiment Analysis',
            backgroundColor: ['mediumseagreen', 'deepskyblue', 'indianred'],
            data: [0, 0, 0]
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
    otherArticles () {
      // ArticleOtherEntities.vue doesn't need the first entity as it is in EntitySpotlight.vue...
      return this.Article.slice(1)
    },
    watchParam () {
      // Dynamically select the parameter to watch.
      return this.$route.params.articleId || this.$route.params.entityId
    }
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend
    this.isLoading = true
    Promise.all([this.fetchArticleSentiments(), this.fetchMiniBingEntity()]).finally(() => {
      const entityIds = this.Article.map(entry => entry.entity_id)
      console.log(entityIds)
      entityIds.map(entityId => this.fetchMiniBingEntity(entityId))
      this.isLoading = false
    })
  },

  methods: {

    formatPublicationDate (dateString) {
      const date = new Date(dateString)
      const formattedDate = format(date, 'eeee do MMMM y')
      return formattedDate
    },

    updateReRender (value) {
      this.re_render = value
    },

    getSubsection (url) {
      // Extract the subsection before the top-level domain
      const match = url.match(/^(https?:\/\/)?(?:www\.)?([^/]+)/)
      const subsection = match ? match[2] : ''
      const maxChars = 15
      return subsection.length > maxChars ? subsection.substring(0, maxChars) + '...' : subsection
    },

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
          console.log(this.Article)

          // 0th entry is always the primary entity in the URL so it matches click throughs
          this.chartdata.datasets[0].data = [data[0].positive, data[0].neutral, data[0].negative]
        })
        .catch((error) => {
          console.error('Error fetching Article info:', error)
        })
    },

    fetchMiniBingEntity (entityId) {
      console.log(entityId)
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
            console.log(data)
            this.bingEntity.push(data)
          } else {
            // Otherwise, I replace the first element with the new data
            console.log(data)
            this.bingEntity.unshift(data)
          }
        })
        .catch((error) => {
          console.error('Error fetching BingEntity:', error)
        })
    }


  }
}
</script>

<style scoped>
.content-container {
  display: flex;
  justify-content: space-around;
  margin: 30px;
}

.flex-box{
  margin: 30px;
}

.article-box {
  border: 1px solid #ccc;
  min-width: 20vw;
  max-width: 50vw;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin: 30px;
}

.article-photo img, .entity-photo img {
  max-width: 90%;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 30px auto;
}

@media screen and (max-width: 1200px) {
  .content-container {
    display: block;
    text-align: center;
    justify-content: center;
  }
}
</style>
