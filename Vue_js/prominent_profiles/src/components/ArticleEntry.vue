<template>
  <div class="article-entry">
    <h2 v-html="entry.headline"></h2>
     <div class="sentiment-bar">
      <div class="positive" :style="{ width: positiveWidth }">{{ positiveWidth }}</div>
      <div class="neutral" :style="{ width: neutralWidth }">{{ neutralWidth }}</div>
      <div class="negative" :style="{ width: negativeWidth }">{{ negativeWidth }}</div>
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
  margin-bottom: 10px;
  border-radius: 5px;
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

</style>
