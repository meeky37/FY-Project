<template>
  <div>
    <div class="card">
      <h2 class="entity-name" @click="redirectToEntityPage">{{ entry.entity_name }}</h2>
    <div class="animated-positive left-box">
      <p class="box-icon">
            <font-awesome-icon :icon="['fas', 'circle-chevron-up']" class="positive" />
          </p>
      <transition-group name="reel" tag="div">
        <p v-if="positiveArticle.length > 0" :key="currentPositiveIndex"
           v-html="removeBoldTags(positiveArticle[currentPositiveIndex].headline)"
           @click="viewArticleDetail(positiveArticle[currentPositiveIndex].id)"
           class="headline">
        </p>
      </transition-group>
    </div>

      <div class="entity-photo-frame">
        <div class="entity-photo">
          <img
            v-if="bingEntity && bingEntity.image_url"
            @click="redirectToEntityPage"
            :src="bingEntity.image_url"
            alt="Entity Photo"
            style="width: auto; min-height: 150px;"
            :title="getAttributionMessage(bingEntity)"
          />
          <a v-if="getAttributionMessage(bingEntity)" class="attribution-link" @mouseover="showAttribution" @mouseleave="hideAttribution"></a>
        </div>
      </div>

    <div class="animated-negative right-box">
      <p class="box-icon">
      <font-awesome-icon :icon="['fas', 'circle-chevron-down']" class="negative" />
    </p>
      <transition-group name="reel" tag="div">
        <p v-if="negativeArticle.length > 0" :key="currentNegativeIndex"
           v-html="removeBoldTags(negativeArticle[currentNegativeIndex].headline)"
           @click="viewArticleDetail(negativeArticle[currentNegativeIndex].id)"
           class="headline">
        </p>
      </transition-group>
    </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/config'
import axios from 'axios'

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
              // this.neutralEntries.push(article) for trending do nothing
            } else {
              this.negativeArticle.push(article)
            }
          })

          // Call sortEntries ONLY after data has been processed
          this.sortEntries()
          console.log('Positive Articles:', this.positiveArticle[0].headline)
          console.log('Negative Articles:', this.negativeArticle[0].headline)
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    },
    sortEntries () {
      // Sort positiveArticle and negativeArticle by publication date as this is a trending view
      // focusing on recent / fresh.
      const sortByDate = (a, b) => new Date(b.publication_date) - new Date(a.publication_date)
      this.positiveArticle.sort(sortByDate)
      this.negativeArticle.sort(sortByDate)
    },

    animateBoxes () {
      setInterval(() => {
        if (this.currentPositiveIndex === 5) {
          this.currentPositiveIndex = 0
        } else if (this.positiveArticle.length > 0) {
          this.currentPositiveIndex =
            (this.currentPositiveIndex + 1) % this.positiveArticle.length
        }
        if (this.currentNegativeIndex === 5) {
          this.currentNegativeIndex = 0
        } else if (this.negativeArticle.length > 0) {
          this.currentNegativeIndex =
            (this.currentNegativeIndex + 1) % this.negativeArticle.length
        }
      }, 5000)
    },

    removeBoldTags (htmlString) {
      return htmlString.replace(/<b>/g, '').replace(/<\/b>/g, '')
    },

    async fetchMiniBingEntity () {
      const id = this.entry.entity_id
      console.log(id)
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/mini/${id}/`

      try {
        const response = await fetch(apiUrl)
        const data = await response.json()

        if (data && Object.keys(data).length > 0) {
          this.bingEntity = data
        } else {
          await this.fetchEntityName(id)
        }
      } catch (error) {
        console.error('Error fetching BingEntity:', error)
        // Bing data may not be available e.g. app_visible is false in db or bing api job not ran yet.
        await this.fetchEntityName(id)
      }
    },

    async fetchEntityName (entityId) {
      const nameApiUrl = `${API_BASE_URL}/profiles_app/entity_name/${entityId}/`

      try {
        const nameResponse = await fetch(nameApiUrl)
        const nameData = await nameResponse.json()

        if (nameData && 'name' in nameData) {
          console.log(nameData.name)
          this.bingEntity = {
            id: entityId,
            name: nameData.name,
            description: null,
            image_url: null,
            web_search_url: `https://www.google.com/search?q=${encodeURIComponent(nameData.name)}`,
            bing_id: null,
            contractual_rules: null,
            entity_type_display_hint: null,
            entity_type_hints: null,
            date_added: null
          }
          console.log(this.bingEntity.web_search_url)
        } else {
          console.error('Entity name not found for ID:', entityId)
        }
      } catch (error) {
        console.error('Error fetching entity name:', error)
      }
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
      if (bingEntity && bingEntity.contractual_rules) {
        const mediaUrl = this.getMediaUrl(bingEntity)
        return `Attribution: ${mediaUrl}`
      } else {
        return 'Attribution: Not available'
      }
    },

    redirectToEntityPage () {
      // Redirect to the URL related to the selected entity
      if (this.entry.entity_id) {
        this.$router.push('/entity/' + this.entry.entity_id)
      }
    },

    viewArticleDetail (articleID) {
      const articleId = articleID
      const entityId = this.entry.entity_id
      this.$router.push({ name: 'entryId', params: { entityId, articleId } })
    }

  }
}
</script>

<style scoped>
  .card {
    position: relative;
    overflow: hidden;
    padding: 15px;
    margin: 15px ;
    border: 1px solid #ddd;
    border-radius: 8px;
    height: 520px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    min-width: 300px;
  }

  .animated-positive, .animated-negative {
    width: 90%;
    height: 150px;
    padding: 0px;
    //border: 1px solid #ddd;
    //border-radius: 8px;
    text-align: center;
    margin-top: 0%;
  }

  .reel-enter-active {
    transition-delay: 0.5s;
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
}

  .entity-name {
    margin-bottom: 0px;
    cursor: pointer;
  }

  .headline {
    cursor: pointer;
  }
</style>
