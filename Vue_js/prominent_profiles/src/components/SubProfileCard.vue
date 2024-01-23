<template>
  <div>
    <div class="card">
      <div class="entity-photo-frame">
        <div class="entity-photo">
          <img
            v-if="bingEntity && bingEntity.image_url"
            @click="redirectToEntityPage"
            :src="bingEntity.image_url"
            alt="Entity Photo"
            style="width: 100px; height: auto; border-radius: 4px;"
            :title="getAttributionMessage(bingEntity)"
          />
          <a v-if="getAttributionMessage(bingEntity)" class="attribution-link" @mouseover="showAttribution" @mouseleave="hideAttribution"></a>
        </div>
      </div>

      <div class="animated-positive">
        <p class="box-icon">
          <font-awesome-icon :icon="['fas', 'circle-chevron-up']" class="positive" />
        </p>
        <p class="sentiment-count">{{ positiveArticle.length }}</p>
      </div>

      <div class="animated-negative">
        <p class="box-icon">
          <font-awesome-icon :icon="['fas', 'circle-chevron-down']" class="negative" />
        </p>
        <p class="sentiment-count">{{ negativeArticle.length }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/config'
import axios from 'axios'
import {
  fetchEntityName,
  fetchMiniBingEntity,
  getAttributionMessage,
  getMediaUrl,
  redirectToEntityPage,
  viewArticleDetail
} from '@/shared_methods/common_requests'

export default {
  props: {
    entry: {
      type: Object,
      required: true
    }
  },

  data () {
    return {
      positiveArticle: [],
      negativeArticle: [],
      currentPositiveIndex: 0,
      currentNegativeIndex: 0,
      bingEntity: null,
      isLoading: false
    }
  },

  mounted () {
    this.fetchMiniBingEntity()
    this.fetchData()
    this.animateBoxes()
  },

  methods: {
    fetchData () {
      const entityId = this.entry.entity_id
      const apiUrl = `${API_BASE_URL}/profiles_app/overall_sentiments/exp/${entityId}/`

      this.positiveArticle = []
      this.negativeArticle = []

      axios.get(apiUrl)
        .then(response => {
          const articles = response.data
          articles.forEach(article => {
            if (parseFloat(article.positive) > parseFloat(article.neutral) && parseFloat(article.positive) > parseFloat(article.negative)) {
              this.positiveArticle.push(article)
            } else if (parseFloat(article.neutral) > parseFloat(article.positive) && parseFloat(article.neutral) > parseFloat(article.negative)) {
              this.neutralEntries.push(article)
            } else {
              this.negativeArticle.push(article)
            }
          })

          // // Call sortEntries ONLY after data has been processed
          // this.sortEntries()
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    },
    // sortEntries () {
    //   // Sort positiveArticle and negativeArticle by publication date as this is a trending view
    //   // focusing on recent / fresh.
    //   const sortByDate = (a, b) => new Date(b.publication_date) - new Date(a.publication_date)
    //   this.positiveArticle.sort(sortByDate)
    //   this.negativeArticle.sort(sortByDate)
    // },

    // animateBoxes () {
    //   setInterval(() => {
    //     if (this.currentPositiveIndex === 5) {
    //       this.currentPositiveIndex = 0
    //     } else if (this.positiveArticle.length > 0) {
    //       this.currentPositiveIndex =
    //         (this.currentPositiveIndex + 1) % this.positiveArticle.length
    //     }
    //     if (this.currentNegativeIndex === 5) {
    //       this.currentNegativeIndex = 0
    //     } else if (this.negativeArticle.length > 0) {
    //       this.currentNegativeIndex =
    //         (this.currentNegativeIndex + 1) % this.negativeArticle.length
    //     }
    //   }, 5000)
    // },

    removeBoldTags (htmlString) {
      return htmlString.replace(/<b>/g, '').replace(/<\/b>/g, '')
    },

    fetchMiniBingEntity,
    fetchEntityName,
    getMediaUrl,
    getAttributionMessage,
    redirectToEntityPage,
    viewArticleDetail

    // async fetchMiniBingEntity () {
    //   const id = this.entry.entity_id
    //   console.log(id)
    //   const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/mini/${id}/`
    //
    //   try {
    //     const response = await fetch(apiUrl)
    //     const data = await response.json()
    //
    //     if (data && Object.keys(data).length > 0) {
    //       this.bingEntity = data
    //     } else {
    //       await this.fetchEntityName(id)
    //     }
    //   } catch (error) {
    //     console.error('Error fetching BingEntity:', error)
    //     // Bing data may not be available e.g. app_visible is false in db or bing api job not ran yet.
    //     await this.fetchEntityName(id)
    //   }
    // },

    // async fetchEntityName (entityId) {
    //   const nameApiUrl = `${API_BASE_URL}/profiles_app/entity_name/${entityId}/`
    //
    //   try {
    //     const nameResponse = await fetch(nameApiUrl)
    //     const nameData = await nameResponse.json()
    //
    //     if (nameData && 'name' in nameData) {
    //       console.log(nameData.name)
    //       this.bingEntity = {
    //         id: entityId,
    //         name: nameData.name,
    //         description: null,
    //         image_url: null,
    //         web_search_url: `https://www.google.com/search?q=${encodeURIComponent(nameData.name)}`,
    //         bing_id: null,
    //         contractual_rules: null,
    //         entity_type_display_hint: null,
    //         entity_type_hints: null,
    //         date_added: null
    //       }
    //       console.log(this.bingEntity.web_search_url)
    //     } else {
    //       console.error('Entity name not found for ID:', entityId)
    //     }
    //   } catch (error) {
    //     console.error('Error fetching entity name:', error)
    //   }
    // },

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
    //   if (bingEntity && bingEntity.contractual_rules) {
    //     const mediaUrl = this.getMediaUrl(bingEntity)
    //     return `Attribution: ${mediaUrl}`
    //   } else {
    //     return 'Attribution: Not available'
    //   }
    // },
    //
    // redirectToEntityPage () {
    //   // Redirect to the URL related to the selected entity
    //   if (this.entry.entity_id) {
    //     this.$router.push('/entity/' + this.entry.entity_id)
    //   }
    // },
    //
    // viewArticleDetail (articleID) {
    //   const articleId = articleID
    //   const entityId = this.entry.entity_id
    //   this.$router.push({ name: 'entryId', params: { entityId, articleId } })
    // }

  }
}
</script>

<style scoped>
  .card {
    position: relative;
    overflow: hidden;
    padding: 15px;
    margin: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-width: 300px;
    height: 520px;
    flex-direction: row
  }

  .entity-photo-frame {
    border: 3px solid #755BB4;
    border-radius: 8px;
    overflow: visible;
  }

  .entity-photo {
    position: relative;
    cursor: pointer;
  }

  .entity-photo img {
    margin: 0;
    width: auto;
    height: 100%;
    vertical-align: bottom;
    border-radius: 4px;
  }

  .animated-positive, .animated-negative {
    width: 20%;
    height: 100%;
    padding: 15px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .sentiment-count {
    font-size: 2em;
  }

  .positive {
    color: mediumseagreen;
    font-size: 2em;
  }

  .negative {
    color: indianred;
    font-size: 2em;
  }

  .neutral {
    color: deepskyblue;
    font-size: 2em;
  }
</style>
