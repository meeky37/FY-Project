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
    <div class="advanced-container">
    <font-awesome-icon
      :icon="['fas', 'calendar-days']"
      @click="toggleDatePicker" style="color: #755BB4;" />
  </div>
  </div>
  <div class="date-picker">
    <VDatePicker
      v-if="isDatePickerVisible"
      v-model.range="dateRange"
      :color="selectedColor"
      :disabled-dates="disabledDates"
      @click="rangeSetCheck"/>
  </div>
  <div>
    <button @click="resetToggles" class="reset-button">Reset</button>
  </div>
<!--  <div v-if="dateRange">-->
<!--      <p>Selected Date Range:</p>-->
<!--      <p>Start Date: {{ dateRange.start }}</p>-->
<!--      <p>End Date: {{ dateRange.end }}</p>-->
<!--    </div>-->
</template>

<script setup>
import { ref } from 'vue'
/* TODO: disable dates older than oldest date too */
const selectedColor = ref('teal')
const currentDate = new Date()
const disabledDates = ref([
  {
    start: new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate() + 1)
  }
])
</script>

<script>
export default {
  emits: ['updateSortType', 'updateDateFilter'],
  props: {
    oldestArticleDate: {
      type: Date,
      default: new Date(2023, 0, 1)
    }
  },

  data () {
    return {
      sortType: 'sentiment', // Default to sentiment
      isAscending: true,
      sortDirectionKey: 0,
      isDatePickerVisible: false,
      dateRange: null,
      previousDateRange: null
    }
  },
  // watch: {
  //   oldestArticleDate(newOldestDate, newOldestDate) {
  //     this.sortEntries()
  //   }
  // },

  watch: {
    '$route.params.id': function (newId, oldId) {
      // console.log('Sort Toggle: Route parameter changed:', newId)
      // newId not defined? e.g. homepage don't attempt new API call.
      if (newId !== undefined) {
        this.$emit('updateSortType', this.sortType, this.isAscending)
        // console.log('Sort Toggle date range: :', this.dateRange)
        this.$emit('updateDateFilter', this.dateRange)
      }
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
      // console.log('icon should change')
      this.$emit('updateSortType', this.sortType, this.isAscending)
    },
    toggleDatePicker () {
      this.isDatePickerVisible = !this.isDatePickerVisible
    },
    rangeSetCheck () {
      if (this.dateRange && this.previousDateRange !== this.dateRange &&
        this.dateRange.start !== null &&
        this.dateRange.end !== null &&
        this.isDatePickerVisible) {
        this.previousDateRange = this.dateRange
        this.$emit('updateDateFilter', this.dateRange)
        this.isDatePickerVisible = !this.isDatePickerVisible
      }
    },
    resetToggles () {
      this.sortType = 'sentiment'
      this.isAscending = true
      this.sortDirectionKey = 0
      this.isDatePickerVisible = false
      this.dateRange = null
      this.previousDateRange = null
      this.$emit('updateSortType', this.sortType, this.isAscending)
      this.$emit('updateDateFilter', this.dateRange)
    }
  }
}
</script>

<style scoped>

.toggle-container {
  display: flex;
  justify-content: center;
  height: 1vh;
}

.advanced-container {
  display: flex;
  display: inline-block;
  font-size: xx-large;
  margin-right: 0px;
  height: auto;
  width: 75px;
  padding-left: 10px;
  padding-right: 10px;
  position: relative;
}

.radio-label {
  cursor: pointer;
  display: inline-block;
  font-size: xx-large;
  margin-right: 0px;
  height: auto;
  width: 75px;
  padding-left: 10px;
  padding-right: 10px;
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

.date-picker {
  position: relative;
  z-index: 1000;
  margin-top: 1%;
  max-height: 1px;
}

.reset-button{
  background-color: #755BB4;
  color: white;
  cursor: pointer;
  font-size: 16px;
  height: 35px;
  padding-left: 10px;
  padding-right: 10px;
  margin-bottom: 10px;
  background-color: #755BB4;
  border-radius: 5px;
}
</style>