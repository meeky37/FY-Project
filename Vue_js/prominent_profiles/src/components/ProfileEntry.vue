<template>
  <div v-if="bingEntity" class="article-entry">
    <div class="entry-content">
      <img v-if="bingEntity.image_url"
           :src="bingEntity.image_url"
           alt="Article Image"
           @click="redirectToEntityPage"
           class="entity-image" />

      <div class="name-container">
        <h2 v-if="bingEntity.name"
            class="name"
            @click="redirectToEntityPage"
        >{{ bingEntity.name }}</h2>

        <div class="url-container">
          <template v-if="bingEntity.web_search_url">
            <div class="external-link">
              <a :href="bingEntity.web_search_url" target="_blank">
                <font-awesome-icon :icon="['fab','google']" style="color: #755BB4;"/>
              </a>
            </div>
          </template>

          <template v-else>
            <div class="internal-link">
              <router-link :to="{ name: 'entity', params: { id: entry.entity_id } }">
                <font-awesome-icon :icon="['fas','magnifying-glass-chart'] " style="color: #755BB4;" />
              </router-link>
            </div>
          </template>
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
import { API_BASE_URL } from '@/config.js'
export default {
  props: {
    entry: {
      type: Object,
      required: true
    }
  },

  data () {
    return {
      bingEntity: null
    }
  },

  created () {
    this.fetchMiniBingEntity()
  },

  methods: {
    async fetchEntityName (entityId) {
      const nameApiUrl = `${API_BASE_URL}/profiles_app/entity_name/${entityId}/`

      try {
        const nameResponse = await fetch(nameApiUrl)
        const nameData = await nameResponse.json()

        if (nameData && 'name' in nameData) {
          console.log(nameData.name)
          this.bingEntity = {
            id: entityId,
            name: nameData.name,
            description: null,
            image_url: null,
            web_search_url: `https://www.google.com/search?q=${encodeURIComponent(nameData.name)}`,
            bing_id: null,
            contractual_rules: null,
            entity_type_display_hint: null,
            entity_type_hints: null,
            date_added: null
          }
          console.log(this.bingEntity.web_search_url)
        } else {
          console.error('Entity name not found for ID:', entityId)
        }
      } catch (error) {
        console.error('Error fetching entity name:', error)
      }
    },

    async fetchMiniBingEntity () {
      const id = this.entry.entity_id
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/mini/${id}/`

      try {
        const response = await fetch(apiUrl)
        if (response.ok) {
          if (response.status !== 204) {
            // Check if the response is not 204 No Content we can link back to their app page
            const data = await response.json()
            if (data && Object.keys(data).length > 0) {
              this.bingEntity = data
            } else {
              // If data is empty but response was successful, trigger this for Goolge url / icon!
              await this.fetchEntityName(id)
            }
          } else {
            // Google fall back
            await this.fetchEntityName(id)
          }
        }
      } catch (error) {
        console.error('Error fetching BingEntity:', error)
        // Handle network errors or errors thrown from response.json()
        await this.fetchEntityName(id)
      }
    },

    isWidthSufficient (width) {
      const minWidthToShowText = 25
      const numericWidth = parseFloat(width)
      return !isNaN(numericWidth) && numericWidth >= minWidthToShowText
    },

    viewArticleDetail () {
      const articleId = this.entry.id
      const entityId = this.$route.params.id
      this.$router.push({ name: 'entryId', params: { entityId, articleId } })
    },

    redirectToEntityPage () {
      // Redirect to the URL related to the selected entity
      if (this.entry.entity_id && this.bingEntity.bing_id !== null) {
        this.$router.push('/entity/' + this.entry.entity_id)
      }
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
<style scoped>
.article-entry {
  border: 1px solid #ccc;
  padding: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
  margin-left: 15px;
  margin-right: 5px;
  border-radius: 25px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
}

.entry-content {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: small;
  flex-wrap: nowrap;
}

.name-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1; /* Adjusted to take available space */
}

.name {
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  cursor: pointer;
}

.entity-image {
  max-width: 48%;
  margin-right: 10px;
  border: 4px solid #755BB4;
  cursor: pointer;
  height: 15vh;
  border: 4px solid #755BB4;
  border-radius: 8px;
}

.internal-link,
.external-link {
  margin-top: 5px;
  text-align: center;
  color: #007bff;
  font-size: x-large;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 5ch;

}

/* TODO: Try non scoped implementation? */
.sentiment-bar {
  display: flex;
  height: 20px;
  margin-top: 10px;
  border-radius: 6px;
  overflow: hidden;
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
  flex-direction: column;
  align-items: center;
  margin-left: 5px;
}

</style>
