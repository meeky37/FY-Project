<template>
  <div class="entity-box">
    <h2>Profile Spotlight</h2>
    <div>
      <h3 v-if="bingEntity[0] && bingEntity[0].name"
          @click="redirectToEntityPage"
          @keyup.enter="redirectToEntityPage"
          class="entity-name"
          tabindex="0"
          >{{ bingEntity[0].name }}</h3>
      <div v-if="bingEntity[0] && bingEntity[0].image_url" class="entity-photo">
        <img
          @click="redirectToEntityPage"
          @keyup.enter="redirectToEntityPage"
          :src="bingEntity[0].image_url"
          alt="Entity Photo"
          tabindex="0"
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
    },

    redirectToEntityPage () {
      // Redirect to the URL related to the selected entity
      if (this.$route.params.entityId) {
        this.$router.push('/entity/' + this.$route.params.entityId)
      }
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
  border: 4px solid #755BB4;
  border-radius: 8px;
  cursor: pointer;
  object-fit: contain;
  margin-bottom: 8%;
}

.entity-name{
  cursor: pointer;
}
</style>
