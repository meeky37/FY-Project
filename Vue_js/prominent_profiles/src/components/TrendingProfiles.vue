<!--<template>-->
<!--  <div>-->
<!--    <div class="card" id="card1">-->
<!--      <img :src="entities[0].photo" alt="Profile Photo" />-->
<!--      <div class="content">-->
<!--        <h2>{{ entities[0].name }}</h2>-->
<!--        <p>{{ entities[0].topPositiveArticle.title }}</p>-->
<!--        <p>{{ entities[0].topNegativeArticle.title }}</p>-->
<!--      </div>-->
<!--    </div>-->

<!--    <div class="card" id="card2">-->
<!--      <img :src="entities[1].photo" alt="Profile Photo" />-->
<!--      <div class="content">-->
<!--        <h2>{{ entities[1].name }}</h2>-->
<!--        <p>{{ entities[1].topPositiveArticle.title }}</p>-->
<!--        <p>{{ entities[1].topNegativeArticle.title }}</p>-->
<!--      </div>-->
<!--    </div>-->

<!--    <div class="card" id="card3">-->
<!--      <img :src="entities[2].photo" alt="Profile Photo" />-->
<!--      <div class="content">-->
<!--        <h2>{{ entities[2].name }}</h2>-->
<!--        <p>{{ entities[2].topPositiveArticle.title }}</p>-->
<!--        <p>{{ entities[2].topNegativeArticle.title }}</p>-->
<!--      </div>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--Replaced above with container / grid layout that adapts better to a range of TrendingProfileCards -->
<!--Works similar to SubProfilesGrid-->
<template>
  <div class="card">
        <div class="grid-container">
    <TrendingProfileCard v-for="(entry) in entities" :key="entry" :entry="entry" />
  </div>
     </div>
</template>

<script setup>
import TrendingProfileCard from './TrendingProfileCard.vue'
import { API_BASE_URL } from '@/config'
import axios from 'axios'
import { ref, onMounted } from 'vue'

const entities = ref([])

const fetchData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/profiles_app/get_trending_entities/`)
    entities.value = response.data.trending_entities.map((item) => ({
      entity_id: item.entity_id,
      entity_name: item.entity_name
    }))
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

onMounted(() => {
  console.log('Component is mounted')
  fetchData()
})

</script>

<style scoped>
  .card {
    position: relative;
    overflow: hidden;
    margin: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    min-height: 20vh;
  }

  img {
    width: 100%;
    height: auto;
    max-height: 100%;
    object-fit: cover;
  }

  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    column-gap: 0px;
    row-gap: 0px;
  }
</style>
