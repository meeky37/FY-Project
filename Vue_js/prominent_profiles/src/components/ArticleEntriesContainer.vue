<template>
  <div class="main-container">
    <div class="sentiment-columns-container">
      <div class="entry-column-icon">
        <p class="column-heading">
  <font-awesome-icon :icon="['fas', 'circle-chevron-up']" class="positive" />
</p>
      </div>
      <div class="entry-column-icon">
       <p class="column-heading">
         <font-awesome-icon :icon="['fas', 'circle-minus']" class="neutral" />
</p>
      </div>
      <div class="entry-column-icon">
          <p class="column-heading">
  <font-awesome-icon :icon="['fas', 'circle-chevron-down']" class="negative" />
</p>
      </div>
    </div>
  </div>
    <div :key="$route.params.id" class="entries-container">
    <div class="entry-column-wrapper">
      <div class="entry-column">
        <!-- Positive Entries -->
        <ArticleEntry v-for="entry in positiveEntries" :key="entry.id" :entry="entry" />
      </div>
    </div>

    <div class="entry-column-wrapper">
      <div class="entry-column">
        <!-- Neutral Entries -->
        <ArticleEntry v-for="entry in neutralEntries" :key="entry.id" :entry="entry" />
      </div>
    </div>

    <div class="entry-column-wrapper">
      <div class="entry-column">
        <!-- Negative Entries -->
        <ArticleEntry v-for="entry in negativeEntries" :key="entry.id" :entry="entry" />
      </div>
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

      this.positiveEntries = []
      this.neutralEntries = []
      this.negativeEntries = []

      axios.get(apiUrl)
        .then(response => {
          const articles = response.data

          articles.forEach(article => {
            if (parseFloat(article.positive) > parseFloat(article.neutral) && parseFloat(article.positive) > parseFloat(article.negative)) {
              this.positiveEntries.push(article)
            } else if (parseFloat(article.neutral) > parseFloat(article.positive) && parseFloat(article.neutral) > parseFloat(article.negative)) {
              this.neutralEntries.push(article)
            } else {
              this.negativeEntries.push(article)
            }
          })

          // Call sortEntries ONLY after data has been processed
          this.sortEntries()
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    },
    sortEntries () {
      console.log('hi ya')
      // Sort positiveEntries, neutralEntries, and negativeEntries
      this.positiveEntries.sort(

        (a, b) => parseFloat(b.positive) - parseFloat(a.positive)
      )
      this.neutralEntries.sort(
        (a, b) => parseFloat(b.neutral) - parseFloat(a.neutral)
      )
      this.negativeEntries.sort(
        (a, b) => parseFloat(b.negative) - parseFloat(a.negative)
      )
    }
  }
}

</script>

<style scoped>
.entries-container {
  display: flex;
  justify-content: center;
}

.entry-column-wrapper {
  flex: 1;
  max-width: calc(33.333% - 25px);
  margin-right: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  background-color: white;
    border-radius: 25px;
}

.entry-column {
  height: 45vh;
  overflow-y: scroll;
  margin-left: 10px;
  margin-top: 10px;
  margin-right: 25px;
  margin-bottom: 1px;
}

.entry-column-icon {
  flex: 1;
  max-width: calc(33.333% - 25px);
  max-height: 50vh;
  overflow-y: auto;
  margin-left: 10px;
  margin-right: 25px;
  margin-bottom: 1px;
}

.main-container {
  display: flex;
  flex-direction: column; /* Align columns vertically */
}

.sentiment-columns-container {
  display: flex;
}

.column-heading {
  font-weight: bold;
  font-size: xx-large;
  position: sticky;
  margin-top: 10px;
  margin-bottom: 10px;
}

.positive {
  color: mediumseagreen;
  font-size: 2em;
}

.neutral {
  color:  deepskyblue;
  font-size: 2em;
}

.negative {
  color:  indianred;
  font-size: 2em;
}

</style>
