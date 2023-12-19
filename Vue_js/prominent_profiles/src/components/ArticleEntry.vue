<template>
  <div class="article-entry">
    <div class="entry-content">
      <img v-if="entry.image_url" :src="entry.image_url" alt="Article Image" class="article-image" />
      <div>
        <h3 v-html="entry.headline"></h3>
       <div v-if="entry.url" class="url-container">
          <div class="url-subsection">
            {{ getSubsection(entry.url) }}
          </div>
          <a :href="entry.url" target="_blank" rel="noopener noreferrer" class="external-link">
            <font-awesome-icon :icon="['fas', 'external-link-alt']" />
          </a>
        </div>
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
export default {
  props: {
    entry: {
      type: Object,
      required: true
    }
  },

  methods: {
    isWidthSufficient (width) {
      const minWidthToShowText = 5
      const numericWidth = parseFloat(width)
      return !isNaN(numericWidth) && numericWidth >= minWidthToShowText
    },

    getSubsection (url) {
      // Extract the subsection before the top-level domain
      const match = url.match(/^(https?:\/\/)?(?:www\.)?([^/]+)/)
      return match ? match[2] : ''
    }
  },
  computed: {
    positiveWidth () {
      const positive = parseFloat(this.entry.positive)
      return isNaN(positive) ? '0%' : `${positive.toFixed(1)}%`
    },
    neutralWidth () {
      const neutral = parseFloat(this.entry.neutral)
      return isNaN(neutral) ? '0%' : `${neutral.toFixed(1)}%`
    },
    negativeWidth () {
      const negative = parseFloat(this.entry.negative)
      return isNaN(negative) ? '0%' : `${negative.toFixed(1)}%`
    }
  }
}
</script>
}

<style scoped>
.article-entry {
  border: 1px solid #ccc;
  padding: 10px;
  margin-top: 0px;
  margin-bottom: 10px;
  margin-left: 15px;
  margin-right: 5px;
  border-radius: 25px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
}

.entry-content {
  display: flex;
  align-items: center;
  font-size: small;
}

.article-image {
  max-width: 48%;
  margin-right: 10px;
  max-height: 200px;
}

.external-link {
  margin-top: 0px;
  color: #007bff;
}

.sentiment-bar {
  display: flex;
  height: 20px;
  margin-top: 10px;
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
  margin-left: 5px;
}

.url-subsection {
  font-size: small;
  color: #777;
  margin-right: 5px;
  display: inline-block;
}

</style>
