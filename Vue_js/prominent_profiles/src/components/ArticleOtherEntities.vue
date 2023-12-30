<template>
  <div class="entity-box">
    <h2>Other Profiles Present*</h2>
    <div>
       <ProfileEntry v-for="entry in Article" :key="entry.id" :entry="entry" />
      </div>
    <p class="bottom-paragraph">*Must be present in at least 20% of the article's sentences</p>
    </div>
</template>

<script>
import 'chart.js/auto'
import ProfileEntry from '@/components/ProfileEntry.vue'

export default {
  props: {
    Article: Array
  },
  components: {
    ProfileEntry
  },

  methods: {
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
  max-height: 80vh;
  overflow: auto;
}

.entity-photo img {
  max-width: 100%;
  height: 10vh;
  border-radius: 8px;
}

.bottom-paragraph {
  margin-top: flex-end;
}
</style>
