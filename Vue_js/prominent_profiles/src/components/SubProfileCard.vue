<template>
  <div class="card">
    <div class="header-container">
      <h2 :class="{ 'loading': isLoading }" @click="redirectToEntityPage(this.lastVisit)">
        {{ isLoading ? 'Loading...' : (bingEntity ? bingEntity.name : 'Loading...') }}
      </h2>
      <div class="sub-button">
      <SubscriptionButton :entityId=" entry ? entry.entity_id : null"/>
        </div>

    </div>
    <div class="content-container">
      <div class="entity-photo-frame">
        <div class="entity-photo">
          <img
            v-if="bingEntity && bingEntity.image_url"
            @click="redirectToEntityPage(this.lastVisit)"
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

      <div class="animated-neutral">
        <p class="box-icon">
          <font-awesome-icon :icon="['fas', 'circle-minus']" class="neutral" />
        </p>
        <p class="sentiment-count">{{ neutralArticle.length }}</p>
      </div>

      <div class="animated-negative">
        <p class="box-icon">
          <font-awesome-icon :icon="['fas', 'circle-chevron-down']" class="negative" />
        </p>
        <p class="sentiment-count">{{ negativeArticle.length }}</p>
      </div>
    </div>
    <div class="news-banner">
  <div class="news-ticker" v-html="concatenatedHeadlines"></div>
</div>
    </div>
</template>

<script>
import { API_BASE_URL } from '@/config'
import SubscriptionButton from '@/components/SubscriptionButton.vue'
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

  components: {
    SubscriptionButton
  },

  data () {
    return {
      positiveArticle: [],
      neutralArticle: [],
      negativeArticle: [],
      currentArticleIndex: 0,
      bingEntity: null,
      isLoading: false,
      currentArticle: null,
      lastVisit: null
    }
  },

  mounted () {
    this.fetchMiniBingEntity()
    this.fetchData()
  },

  computed: {
    allArticles () {
      const combinedArticles = [...this.positiveArticle, ...this.neutralArticle, ...this.negativeArticle]
      const sortByDate = (a, b) => new Date(b.publication_date) - new Date(a.publication_date)
      return combinedArticles.sort(sortByDate)
    },
    concatenatedHeadlines () {
      let string =
        this.allArticles.map(article => this.removeBoldTags(article.headline)).join(' • ')
      string = ' • ' + string
      return string
    }
  },
  methods: {
    fetchData () {
      const entityId = this.entry.entity_id
      const apiUrl = `${API_BASE_URL}/profiles_app/overall_sentiments/exp/${entityId}/?dashboard=true`

      this.positiveArticle = []
      this.neutralArticle = []
      this.negativeArticle = []

      axios.get(apiUrl, { withCredentials: true })
        .then(response => {
          const { data: articles, lastVisit } = response.data
          this.lastVisit = lastVisit
          console.log(this.lastVisit)
          articles.forEach(article => {
            if (parseFloat(article.positive) > parseFloat(article.neutral) && parseFloat(article.positive) > parseFloat(article.negative)) {
              this.positiveArticle.push(article)
            } else if (parseFloat(article.neutral) > parseFloat(article.positive) && parseFloat(article.neutral) > parseFloat(article.negative)) {
              this.neutralArticle.push(article)
            } else {
              this.negativeArticle.push(article)
            }
          })

          // // Call sortEntries ONLY after data has been processed
          this.sortEntries()
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
      this.neutralArticle.sort(sortByDate)
      this.negativeArticle.sort(sortByDate)
    },

    removeBoldTags (htmlString) {
      return htmlString.replace(/<b>/g, '').replace(/<\/b>/g, '')
    },

    fetchMiniBingEntity,
    fetchEntityName,
    getMediaUrl,
    getAttributionMessage,
    redirectToEntityPage,
    viewArticleDetail
  }
}
</script>

<style scoped>
  .card {
    position: relative;
    overflow: hidden;
    margin: 0px;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 275px;
    width:400px;
    flex-direction: column;
  }

  .content-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
.sentiment-count {
  font-size: 1.5em;
}

.entity-photo img {
  max-height: 80%;
}

.entity-photo-frame {
  border: 3px solid #755BB4;
  border-radius: 8px;
  overflow: visible;
  margin-left: 20px;
  margin-bottom: 5px;
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

.animated-positive, .animated-negative, .animated-neutral {
  display: flex;
  flex-direction: column;
  justify-content: center; /* Center items vertically inside the mid-section of the sub card */
  align-items: center;
  height: auto;
}
.header-container h2 {
  margin-left: 50px;
  cursor: pointer;
}
.sentiment-count {
  font-size: 2em;
}

  .box-icon {
    margin: 20px;
  }

  .positive {
    color: mediumseagreen;
    font-size: 2em;
    margin-top: 10px;
  }

  .negative {
    color: indianred;
    font-size: 2em;
    margin-top: 10px;
  }

  .neutral {
    color: deepskyblue;
    font-size: 2em;
    margin-top: 10px;
  }

  .header-container{
    display: flex;
    flex-direction: row;
    height:20px;
    width: auto;
    white-space: nowrap;
    margin-bottom: 20px;
  }

  .sub-button {
    margin-top: 20px;
  }
.news-banner {
  overflow: visible;
  white-space: nowrap;
  position: relative;
  width: 100%;
  height: 50px;
  margin-top: -7px;
}

.news-ticker {
  display: block; /* Ensures the ticker takes up the full width for its content */
  white-space: nowrap;
  position: relative;
  width: auto;
  animation: scroll-news linear infinite;
  animation-duration: 250s; /* Adjust based on desired speed */
  font-size: x-large;
}

@keyframes scroll-news {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(-5000%);
  }
}
</style>
