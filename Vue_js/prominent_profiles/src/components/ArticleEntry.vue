<template>
  <div class="article-entry">
    <div class="entry-content">
      <img v-if="entry.image_url" :src="entry.image_url" alt="Article Image" class="article-image" />
      <div>
        <h3 v-html="entry.headline" class="headline"></h3>
       <div v-if="entry.url" class="url-container">
         <div class="button-container" @click="viewArticleDetailArticleEntry"
              @keyup.enter="viewArticleDetailArticleEntry" tabindex="0">
          <font-awesome-icon :icon="['fas', 'magnifying-glass-chart']" style="color: #755BB4;"/>
          </div>
          <div class="url-subsection">
            {{ getSubsection(entry.url, substringLength) }}
          </div>
          <a :href="entry.url" target="_blank" rel="noopener noreferrer" class="external-link">
            <font-awesome-icon :icon="['fas', 'external-link-alt']" />
          </a>
        </div>
        <p class="date">{{ formatPublicationDate(entry.publication_date) }}</p>
      </div>
    </div>
    <div class="sentiment-bar">
        <div class="positive" :style="{ width: positiveWidth }">
      <template v-if="isWidthSufficient(positiveWidth)">{{ positiveWidth }}</template>
    </div>
    <div class="neutral" :style="{ width: neutralWidth }">
      <template v-if="isWidthSufficient(neutralWidth)">{{ neutralWidth }}</template>
    </div>
    <div class="negative" :style="{ width: negativeWidth }">
      <template v-if="isWidthSufficient(negativeWidth)">{{ negativeWidth }}</template>
    </div>
    </div>
  </div>
</template>
<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { format } from 'date-fns'
import { useRouter, useRoute } from 'vue-router'
import { getSubsection } from '../shared_methods/common_requests.js'

export default {
  props: {
    entry: {
      type: Object,
      required: true
    }
  },
  setup (props) {
    const router = useRouter()
    const route = useRoute()

    const formatPublicationDate = (dateString) => {
      const date = new Date(dateString)
      return format(date, 'do MMM')
    }

    const isWidthSufficient = (width) => {
      const minWidthToShowText = 15
      const numericWidth = parseFloat(width)
      return !isNaN(numericWidth) && numericWidth >= minWidthToShowText
    }

    const viewArticleDetailArticleEntry = () => {
      const articleId = props.entry.id
      console.log(props.entry)
      const entityId = route.params.id
      router.push({ name: 'entryId', params: { entityId, articleId } })
    }

    const positiveWidth = computed(() => {
      const positive = parseFloat(props.entry.positive)
      return isNaN(positive) ? '0%' : `${positive.toFixed(1)}%`
    })

    const neutralWidth = computed(() => {
      const neutral = parseFloat(props.entry.neutral)
      return isNaN(neutral) ? '0%' : `${neutral.toFixed(1)}%`
    })

    const negativeWidth = computed(() => {
      const negative = parseFloat(props.entry.negative)
      return isNaN(negative) ? '0%' : `${negative.toFixed(1)}%`
    })

    const windowWidth = ref(window.innerWidth)

    const handleResize = () => {
      windowWidth.value = window.innerWidth
    }

    onMounted(() => {
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    /* Making article source credit text cut off depending on available space */
    const substringLength = computed(() => {
      if (windowWidth.value <= 500) {
      /* Card containers are vertically stacked at this point but mobile! */
        return 7
      } else if (windowWidth.value <= 1275) {
      /* Card containers are vertically stacked at this point */
        return 20
      } else if (windowWidth.value <= 1350) {
        /* Card containers are in a row at this point and above */
        return 10
      } else if (windowWidth.value <= 1650) {
        return 15
      } else {
        return 20
      }
    })

    return {
      formatPublicationDate,
      isWidthSufficient,
      getSubsection,
      substringLength,
      viewArticleDetailArticleEntry,
      positiveWidth,
      neutralWidth,
      negativeWidth
    }
  }
}
</script>

<style scoped>
.article-entry {
  border: 1px solid #ccc;
  padding: 10px;
  margin: 10px 5px 10px 15px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.entry-content {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: small;
  flex-wrap: nowrap;

}

.headline {
  overflow: hidden;
  text-overflow: ellipsis;
  justify-content: right;
  flex: 1;
  font-size: small;
  max-width: 88%;
}

.article-image {
  max-width: 45%;
  margin-right: 10px;
  justify-content: left;
  flex: 1;
}

.external-link {
  margin-top: 0px;
  color: #007bff;
  font-size: large;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 5ch;
}

.button-container{
  margin-left: 0px;
  margin-right: 10px;
  font-size: x-large;
}

.sentiment-bar {
  display: flex;
  height: 20px;
  margin-top: 10px;
  border-radius: 6px;
  overflow: hidden;
}

.positive {
  background-color: mediumseagreen;
  color: white;
  text-align: center;
}

.neutral {
  background-color: deepskyblue;
  color: white;
  text-align: center;
}

.negative {
  background-color: indianred;
  color: white;
  text-align: center;
}

.url-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0px;
}

.url-subsection {
  font-size: small;
  color: #777;
  margin-right: 5px;
  display: inline-block;
}

</style>
