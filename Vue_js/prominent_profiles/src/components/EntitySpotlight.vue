<template>
  <div class="entity-box">
    <h2>Profile Spotlight</h2>
    <div>
      <h3 v-if="bingEntity[0] && bingEntity[0].name">{{ bingEntity[0].name }}</h3>
      <div v-if="bingEntity[0] && bingEntity[0].image_url" class="entity-photo">
        <img
          :src="bingEntity[0].image_url"
          alt="Entity Photo"
        />
        <p v-if="bingEntity[0] && bingEntity[0].display_hint">{{ bingEntity[0].display_hint }}</p>
        <div v-if="re_render" class="chart-container">
          <Doughnut ref="doughnutChart" :data="chartdata" :options="options" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Doughnut } from 'vue-chartjs'
import 'chart.js/auto'

export default {
  props: {
    bingEntity: Array,
    chartdata: Object,
    options: Object,
    re_render: Boolean
  },
  components: {
    Doughnut
  },

  methods: {
    async forcedReRender () {
      this.$emit('updateReRender', false)
    }
  },
  watch: {
    // Watching for changes in chartdata
    chartdata: {
      handler () {
        this.forcedReRender().then(() => {
          this.$emit('updateReRender', true)
        })
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.entity-box {
  border: 1px solid #ccc;
  min-width: 20vw;
  max-width: 50vw;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.entity-photo img {
  max-width: 100%;
  height: 15vh;
  border-radius: 8px;
}
</style>
