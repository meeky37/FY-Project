<template>
  <div>
     <div class="header-container">
      <h1 :class="{ 'loading': isLoading }">{{ isLoading ? 'Loading...' : (bingEntity ? bingEntity.name : 'Entity Not Found') }}</h1>
      <SubscriptionButton :entityId="$route.params.id"/>
    </div>

    <!-- Display the image and description (centered) -->
    <div v-if="bingEntity && !isLoading" class="content-container">
      <div class="entity-photo">
        <img
          :src="bingEntity.image_url"
          alt="Entity Photo"
          style="width: auto; min-height: 150px; border-radius: 8px; border: 4px solid #755BB4;"
          :title="getAttributionMessage(bingEntity)"
        />
         <a class="attribution-link" @click="openSourcePopup">CREDIT</a>
      </div>

      <div class="description-box">
        <p>{{ bingEntity.description }}</p>
        <p class="source-date">
            <a :href="getDescriptionUrl(bingEntity)" target="_blank">Wikipedia</a>
            <br>
            {{ formatDate(bingEntity.date_added) }}
          </p>
      </div>
    </div>

    <div v-if="showSourcePopup" class="source-popup">
      <p>
        Original Image Source:
        <a :href="getMediaUrl(bingEntity)" target="_blank">{{ getMediaUrl(bingEntity) }}</a>
      </p>
      <button @click="closeSourcePopup">Close</button>
    </div>

    <div class="sort-toggle">
    <SortToggle @updateSortType="updateSortType"
                @updateDateFilter="updateDateFilter"
                :oldestArticleDate="oldestArticleDate" />
    </div>
    <!-- Use ArticleEntriesContainer to display entries -->
    <ArticleEntriesContainer
      :sortType ="sortType"
      :isAscending="isAscending"
      :dateRange="dateRange"
      @oldestArticleDate="setOldestArticleDate"/>
  </div>
</template>

<script>
import ArticleEntriesContainer from '../components/ArticleEntriesContainer.vue'
import SortToggle from '@/components/SortToggle.vue'
import { API_BASE_URL } from '@/config.js'
import VueCookie from 'vue-cookie'
import SubscriptionButton from '@/components/SubscriptionButton.vue'
export default {
  name: 'EntityPage',

  components: {
    SubscriptionButton,
    ArticleEntriesContainer,
    SortToggle
  },

  data () {
    return {
      bingEntity: null,
      isLoading: false,
      showSourcePopup: false,
      sortType: 'sentiment',
      isAscending: true,
      oldestArticleDate: null,
      dateRange: null
    }
  },
  watch: {
    '$route.params.id': function (newId, oldId) {
      console.log('Route parameter changed:', newId)
      // Check if newId is defined before triggering bing entity
      if (newId !== undefined) {
        this.fetchBingEntity()
      }
    }
  },

  created () {
    // Fetch BingEntity JSON based on the entity ID from Django backend
    this.fetchBingEntity()
    const viewedProfilesCookie = VueCookie.get('viewedProfiles')

    if (viewedProfilesCookie === null) {
      // Set the cookie to an empty array if it doesn't exist
      VueCookie.set('viewedProfiles', [])
    }
  },

  methods: {
    openSourcePopup () {
      this.showSourcePopup = true
    },
    closeSourcePopup () {
      this.showSourcePopup = false
    },

    async incrementViewCount (entityId) {
      try {
        // Check if the user has already viewed the profile in the current session
        // JSON.parse converts the string to an array
        const viewedProfiles = JSON.parse(VueCookie.get('viewedProfiles') || '[]')

        if (viewedProfiles.includes(entityId.toString())) {
          console.log(`Already viewed in this session: ${entityId}`)
          return
        }

        const csrfToken = VueCookie.get('csrftoken')
        // console.log('token...')
        // console.log(csrfToken)
        // const response = await fetch(`${API_BASE_URL}/profiles_app/increment_view_count/${entityId}/`, {
        const response = await
        fetch(`${API_BASE_URL}/profiles_app/create_entity_view/${entityId}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          credentials: 'include'
        })

        if (response.ok) {
          console.log(`View count incremented for entity ${entityId}`)
          // Cookie here to track viewed profiles in the current session
          // Use JSON.stringify to convert the array to a string
          VueCookie.set('viewedProfiles', JSON.stringify([...viewedProfiles, entityId]), { expires: 1 })
          console.log(JSON.stringify(VueCookie.get('viewedProfiles')))
          // expire in 1 day ppl don't close browsers much these days.
        } else {
          console.log('Error incrementing view count:', response.statusText)
        }
      } catch (error) {
        console.error('Error incrementing view count:', error)
      }
    },

    fetchBingEntity () {
      this.isLoading = true
      // Use the entity ID from the route parameters
      const entityId = this.$route.params.id

      // Fetch BingEntity JSON from Django backend
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/${entityId}/`

      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          this.bingEntity = data
          this.incrementViewCount(entityId) // for trending entities feature
        })
        .catch((error) => {
          console.error('Error fetching BingEntity:', error)
        })
        .finally(() => {
          this.isLoading = false
        })
    },

    getMediaUrl (bingEntity) {
    // Extract description URL from contractual rules
      const mediaContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/MediaAttribution' &&
        rule.targetPropertyName === 'image'
      )

      const mediaUrl = mediaContract ? mediaContract.url : null
      return mediaUrl
    },

    getAttributionMessage (bingEntity) {
      const mediaUrl = this.getMediaUrl(bingEntity)
      return `Attribution: ${mediaUrl}`
    },

    getDescriptionUrl (bingEntity) {
      // Extract description URL from contractual rules
      const descriptionContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
          rule.targetPropertyName === 'description'
      )
      return descriptionContract ? descriptionContract.url : '#'
    },

    getDescriptionSource (bingEntity) {
      // Extract description source text from contractual rules
      const descriptionContract = bingEntity.contractual_rules.find(
        (rule) => rule._type === 'ContractualRules/LinkAttribution' &&
          rule.targetPropertyName === 'description'
      )
      return descriptionContract ? descriptionContract.text : 'Unknown Source'
    },

    formatDate (dateString) {
      // Format the date string as desired
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      const date = new Date(dateString)
      return date.toLocaleDateString(undefined, options)
    },

    updateSortType (newSortType, newIsAscending) {
      // console.log('updateSortType emit triggered in Entity Page!')
      this.sortType = newSortType
      this.isAscending = newIsAscending
    },

    updateDateFilter (newDateRange) {
      // console.log('updateDateFilter emit triggered in Entity Page!')
      this.dateRange = newDateRange
    },

    setOldestArticleDate (newArticleDate, oldArticleDate) {
      console.log(newArticleDate)
      this.oldestArticleDate = newArticleDate
    }
  }
}
</script>

<style scoped>

.content-container {
  display: flex;
  align-items: center;
}

.entity-photo {
  margin-left: 30px;
  max-width: 300px;
  max-height: 300px;
}

.description-box {
  background-color: #f4f4f4;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin: 0px 30px 0px 30px;
  position: relative;
  min-width: 75vw;
}
.description-box p {
  font-size: medium;
  line-height: 1.6;
  color: #333;
}

.source-date {
  font-size: xx-small;
  text-align: right;
  margin-right: 5px;
  margin-bottom: 0px;
  position: absolute;
  bottom: 0;
  right: 0;
}

.source-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

.source-popup a {
  color: blue;
  text-decoration: underline;
  margin-left: 5px;
  z-index: 9999;
}

.source-popup button {
  margin-top: 10px;
}

.attribution-link{
  font-size: small;
  color: purple;
  text-decoration: underline;
  cursor: pointer;
}

.attribution-link:hover {
  color: purple;
}

.sort-toggle{
  position: relative;
  z-index: 9998;
  overflow: visible;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

h1 {
  margin-right: 10px;
}

</style>
