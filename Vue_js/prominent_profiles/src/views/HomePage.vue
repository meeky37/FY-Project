<template>
  <h1>Trending Profiles</h1>
  <div>
    <TrendingProfileList/>
  </div>
   <PageFooter/>
</template>

<script setup>
import TrendingProfileList from '../components/TrendingProfiles.vue'
import PageFooter from '@/components/PageFooter.vue'
</script>
