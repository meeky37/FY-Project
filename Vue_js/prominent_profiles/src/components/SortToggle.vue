<template>
<!--  Sort Type Toggle-->
  <div class="toggle-container">
    <label class="radio-label" @click="selectSortType('sentiment')">
      <input type="radio" v-model="sortType" value="sentiment" class="radio-input" />
      <div :class="{ selected: sortType === 'sentiment' }">
        <font-awesome-icon :icon="['fas', 'percent']" style="color: #755BB4;"/>
      </div>
    </label>
    <label class="radio-label" @click="selectSortType('date')">
      <input type="radio" v-model="sortType" value="date" class="radio-input" />
      <div :class="{ selected: sortType === 'date' }">
         <font-awesome-icon :icon="['fas', 'clock']" style="color: #755BB4;" />
      </div>
    </label>
    <!-- Ordering Toggle -->
    <div class="radio-label" @click="toggleSortDirection" :key="sortDirectionKey">
      <font-awesome-icon :icon="sortDirectionIcon" style="color: #755BB4;" />
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      sortType: 'sentiment', // Default to sentiment
      isAscending: true,
      sortDirectionKey: 0
    }
  },
  computed: {
    sortDirectionIcon () {
      return this.isAscending ? ['fas', 'arrow-up'] : ['fas', 'arrow-down']
    }
  },
  methods: {
    selectSortType (type) {
      this.sortType = type
      this.$emit('updateSortType', this.sortType, this.isAscending)
    },
    toggleSortDirection () {
      this.isAscending = !this.isAscending
      this.sortDirectionKey += 1
      console.log('icon should change')
      this.$emit('updateSortType', this.sortType, this.isAscending)
    }
  }
}
</script>

<style scoped>

.toggle-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.radio-label {
  cursor: pointer;
  display: inline-block;
  font-size: xx-large;
  margin-right: 0px;
  height: auto;
  width: 75px;
  padding: 10px;
  cursor: pointer;
}

.radio-input {
  display: none; /* FAS icons take place of radio buttons */
}

.selected {
  background-color:  #30d5c8;
  border-radius: 5px;
}

.toggle-container {
  cursor: pointer;
  display: inline-block;
  font-size: xx-large;
}

</style>
