<template>
  <div>
<!--    <img :src="entity.photo" alt="entity Photo" />-->
    <div class="card">
      <h2>{{ entity.name }}</h2>
      <p v-if="positiveArticle && positiveArticle.length > 0">
        {{ positiveArticle[0].headline }}
      </p>
      <p v-if="positiveArticle && positiveArticle.length > 1">
        {{ positiveArticle[1].headline }}
      </p>
      <p v-if="positiveArticle && positiveArticle.length > 2">
        {{ positiveArticle[2].headline }}
      </p>

      <p v-if="negativeArticle && negativeArticle.length > 0">
        {{ negativeArticle[0].headline }}
      </p>
      <p v-if="negativeArticle && negativeArticle.length > 1">
        {{ negativeArticle[1].headline }}
      </p>
      <p v-if="negativeArticle && negativeArticle.length > 2">
        {{ negativeArticle[2].headline }}
      </p>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/config'
import axios from 'axios'

export default {
  props: {
    entity: {
      type: Object,
      required: true
    }
  },

  data () {
    return {
      positiveArticle: [],
      negativeArticle: [],
    }
  },

  mounted () {
    this.fetchData()
  },

  methods: {
    fetchData () {
      const entityId = this.entity.id
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
           console.log('Positive Articles:', this.positiveArticle[0].headline);
           console.log('Negative Articles:', this.negativeArticle[0].headline);
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

    }
  }
}

</script>

<style>
  .card {
    position: relative;
    overflow: hidden;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    min-height: 40vh;
    transition: height 0.5s ease;
  }
</style>
