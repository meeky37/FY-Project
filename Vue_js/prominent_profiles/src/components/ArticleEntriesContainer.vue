<template>
  <div class="main-container">
    <div class="sentiment-columns-container">
      <div class="column-container">
        <div class="entry-column-icon">
          <p class="column-heading">
            <font-awesome-icon :icon="['fas', 'circle-chevron-up']" class="positive" />
          </p>
        </div>
        <div class="entry-column-wrapper">
          <div class="entry-column">
            <!-- Positive Entries -->
            <ArticleEntry v-for="entry in positiveEntries" :key="entry.id" :entry="entry" />
          </div>
        </div>
      </div>

      <div class="column-container">
        <div class="entry-column-icon">
          <p class="column-heading">
            <font-awesome-icon :icon="['fas', 'circle-minus']" class="neutral" />
          </p>
        </div>
        <div class="entry-column-wrapper">
          <div class="entry-column">
            <!-- Neutral Entries -->
            <ArticleEntry v-for="entry in neutralEntries" :key="entry.id" :entry="entry" />
          </div>
        </div>
      </div>

      <div class="column-container">
        <div class="entry-column-icon">
          <p class="column-heading">
            <font-awesome-icon :icon="['fas', 'circle-chevron-down']" class="negative" />
          </p>
        </div>
        <div class="entry-column-wrapper">
          <div class="entry-column">
            <!-- Negative Entries -->
            <ArticleEntry v-for="entry in negativeEntries" :key="entry.id" :entry="entry" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleEntry from './ArticleEntry.vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'

export default {

  props: {
    sortType: {
      type: String,
      default: 'sentiment'
    },
    isAscending: {
      type: Boolean,
      default: true
    },
    oldestArticleDate: Date,
    dateRange: Object
  },

  data () {
    return {
      positiveEntries: [],
      neutralEntries: [],
      negativeEntries: [],
      originalPositiveEntries: [],
      originalNeutralEntries: [],
      originalNegativeEntries: []
    }
  },

  mounted () {
    this.fetchData(true)
    this.fetchData()
  },

  watch: {
    '$route.params.id': function (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // newId not defined? e.g. homepage don't attempt new API call.
      if (newId !== undefined) {
        // Changed entity path get new data (contains sort + date filter)
        this.fetchData(true)
        this.fetchData()
      }
    },
    sortType (newSortType, oldSortType) {
      this.sortEntries()
    },
    isAscending (newIsAscending, oldIsAscending) {
      this.sortEntries()
    },
    dateRange (newDateRange, oldDateRange) {
      this.filterEntries()
    }
  },
  components: {
    ArticleEntry
  },

  methods: {
    fetchData (quick = false) {
      const entityId = this.$route.params.id
      // Start from day 0 for quick, and day 15 for the full fetch
      const startDay = quick ? 0 : 15
      // Time period for the API call is based on the 'quick' flag
      const endDay = quick ? 14 : 180
      const apiUrl =
          `${API_BASE_URL}/profiles_app/overall_sentiments/exp/${entityId}/?endDay=${endDay}/?startDay=${startDay}`

      this.positiveEntries = []
      this.neutralEntries = []
      this.negativeEntries = []

      axios.get(apiUrl)
        .then(response => {
          const { data: articles } = response.data

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
          this.setOldestArticleDate()
          this.originalPositiveEntries = this.positiveEntries
          this.originalNeutralEntries = this.neutralEntries
          this.originalNegativeEntries = this.negativeEntries
          this.filterEntries()
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    },

    sortEntries () {
      // Sort positiveEntries, neutralEntries, and negativeEntries

      if (this.sortType === 'date') {
        const sortByDate = (a, b) => new Date(b.publication_date) - new Date(a.publication_date)
        this.positiveEntries.sort(sortByDate)
        this.neutralEntries.sort(sortByDate)
        this.negativeEntries.sort(sortByDate)
      } else {
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
      if (!this.isAscending) {
        this.positiveEntries.reverse()
        this.neutralEntries.reverse()
        this.negativeEntries.reverse()
      }
    },

    getOldestArticle () {
      const sortByDate = (a, b) => new Date(a.publication_date) - new Date(b.publication_date)
      const allEntries = [...this.positiveEntries, ...this.neutralEntries, ...this.negativeEntries]
      allEntries.sort(sortByDate)
      return allEntries[0]
    },

    setOldestArticleDate () {
      const oldestArticle = this.getOldestArticle()
      const dateObject = new Date(oldestArticle.publication_date)
      this.$emit('oldestArticleDate', dateObject)
    },

    filterEntries () {
      // Are both start and end dates are defined in the dateRange?
      if (this.dateRange && this.dateRange.start && this.dateRange.end) {
        // Filter positiveEntries based on the date range
        this.positiveEntries = this.originalPositiveEntries.filter(entry =>
          new Date(entry.publication_date) >= this.dateRange.start &&
          new Date(entry.publication_date) <= this.dateRange.end
        )

        // As above for neutral
        this.neutralEntries = this.originalNeutralEntries.filter(entry =>
          new Date(entry.publication_date) >= this.dateRange.start &&
          new Date(entry.publication_date) <= this.dateRange.end
        )

        // As above for negative
        this.negativeEntries = this.originalNegativeEntries.filter(entry =>
          new Date(entry.publication_date) >= this.dateRange.start &&
          new Date(entry.publication_date) <= this.dateRange.end
        )
      } else {
        this.positiveEntries = this.originalPositiveEntries
        this.neutralEntries = this.originalNeutralEntries
        this.negativeEntries = this.originalNegativeEntries
      }
    }
  }
}

</script>
<style scoped>

.entry-column-wrapper {
  flex: 1 0 calc(33.333% - 25px);
  min-width: 200px;
  margin-left: 15px;
  margin-right: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  background-color: white;
  border-radius: 25px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.entry-column {
  height: 70vh;
  overflow-y: scroll;
  overflow-x: hidden;
  margin-left: 10px;
  margin-top: 10px;
  margin-right: 25px; /* Stops scroll bar hanging out of container on right side */
  margin-bottom: 1px;
  flex-wrap: wrap;
  min-height: 70vh;
  //min-width: 20vw;
  max-width: 750px;
}

.entry-column-icon {
  flex: 1 0 calc(33.333% - 25px);
  max-height: 50vh;
  overflow-y: auto;
  margin-left: 10px;
  margin-right: 10px;
  margin-bottom: 1px;
  flex-wrap: wrap;
}

.main-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.sentiment-columns-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
}

.column-container{
  width: calc(33.333% - 25px);
  flex-wrap: wrap;
}

.column-heading {
  font-weight: bold;
  font-size: xx-large;
  position: sticky;
  margin-top: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.positive {
  color: mediumseagreen;
  font-size: 2em;
}

.neutral {
  color: deepskyblue;
  font-size: 2em;
}

.negative {
  color: indianred;
  font-size: 2em;
}

@media screen and (max-width: 1275px) {
  .sentiment-columns-container {
    display: block; /* Changing to a different layout for small screens/mobile? */
  }

  .column-container {
    width: 100%; /* Occupying full width on smaller screens */
  }

  .entry-column-wrapper{ /* See if larger margin helps scrolling on phone */
    margin-left: 25px;
    margin-right: 25px;
  }
}
</style>
