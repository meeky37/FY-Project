<template>
  <div :key="$route.params.id" class="entries-container">
    <div class="entry-column">
      <p class="column-heading">Positive</p>
      <ArticleEntry v-for="entry in positiveEntries" :key="entry.id"  :entry="entry" />
    </div>

    <div class="entry-column">
      <p class="column-heading">Neutral</p>
      <ArticleEntry v-for="entry in neutralEntries" :key="entry.id" :entry="entry" />
    </div>

    <div class="entry-column">
      <p class="column-heading">Negative</p>
      <ArticleEntry v-for="entry in negativeEntries" :key="entry.id" :entry="entry" />
    </div>
  </div>
</template>

<script>
import ArticleEntry from './ArticleEntry.vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'

export default {

  data () {
    return {
      positiveEntries: [],
      neutralEntries: [],
      negativeEntries: []
    }
  },
  mounted () {
    this.fetchData()
  },

  watch: {
    '$route.params.id': function (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // newId not defined? e.g. homepage don't attempt new API call.
      if (newId !== undefined) {
        this.fetchData()
      }
    }
  },
  components: {
    ArticleEntry
  },

  methods: {
    fetchData () {
      const entityId = this.$route.params.id
      const apiUrl = `${API_BASE_URL}/profiles_app/overall_sentiments/exp/${entityId}/`
      // Can be swapped out for linear figures - see backend.
      // Const apiUrl = `${API_BASE_URL}/profiles_app/overall_sentiments/lin/${entityId}/`

      this.positiveEntries = []
      this.neutralEntries = []
      this.negativeEntries = []
      axios.get(apiUrl)
        .then(response => {
          // Response data is an array of objects
          const articles = response.data

          // Classify articles (client side) based on sentiment scores
          articles.forEach(article => {
            if (parseFloat(article.positive) > parseFloat(article.neutral) && parseFloat(article.positive) > parseFloat(article.negative)) {
              this.positiveEntries.push(article)
            } else if (parseFloat(article.neutral) > parseFloat(article.positive) && parseFloat(article.neutral) > parseFloat(article.negative)) {
              this.neutralEntries.push(article)
            } else {
              this.negativeEntries.push(article)
            }
          })
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    }
  }
}
</script>

<style scoped>
.entries-container {
  display: flex;
}

.entry-column {
  flex: 1;
  max-width: calc(33.333% - 25px);
  max-height: 600px;
  overflow-y: auto;
  margin-right: 10px;
}

.column-heading {
  font-weight: bold;
  font-size: xx-large;
}

</style>
