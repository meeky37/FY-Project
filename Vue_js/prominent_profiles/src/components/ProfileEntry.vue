<template>
<!--  Other profiles may be present but have since been deleted or merged from db so v-if check -->
  <div v-if="bingEntity" class="article-entry">
    <div class="entry-content">
      <img v-if="bingEntity.image_url" :src="bingEntity.image_url" alt="Article Image"
           class="entity-image" />
      <div>
        <h2 v-if="bingEntity.name" class="name">{{ bingEntity.name }}</h2>
       <div v-if="entry.entity_id" class="url-container">
          <router-link :to="{ name: 'entity', params: { id: entry.entity_id } }"
                       class="external-link">
            <font-awesome-icon :icon="['fas','magnifying-glass-chart']" />
          </router-link>
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
    async fetchMiniBingEntity () {
      const id = this.entry.entity_id
      const apiUrl = `${API_BASE_URL}/profiles_app/bing_entities/mini/${id}/`

      try {
        const response = await fetch(apiUrl)
        const data = await response.json()

        if (data && Object.keys(data).length > 0) {
          this.bingEntity = data
        } else {
          await this.fetchEntityName(id)
        }
      } catch (error) {
        console.error('Error fetching BingEntity:', error)
        // Bing data may not be available e.g. app_visible is false in db or bing api job not ran yet.
        await this.fetchEntityName(id)
      }
    },

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
            web_search_url: null,
            bing_id: null,
            contractual_rules: null,
            entity_type_display_hint: null,
            entity_type_hints: null,
            date_added: null
          }
        } else {
          console.error('Entity name not found for ID:', entityId)
        }
      } catch (error) {
        console.error('Error fetching entity name:', error)
      }
    },

    isWidthSufficient (width) {
      const minWidthToShowText = 15
      const numericWidth = parseFloat(width)
      return !isNaN(numericWidth) && numericWidth >= minWidthToShowText
    },

    viewArticleDetail () {
      const articleId = this.entry.id
      const entityId = this.$route.params.id
      this.$router.push({ name: 'entryId', params: { entityId, articleId } })
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

.name {
  overflow: hidden;
  text-overflow: ellipsis;
  justify-content: right;
  flex: 1;
  //font-size: small;

}

.entity-image {
  max-width: 48%;
  margin-right: 10px;
  justify-content: left;
  flex: 1;
}

.external-link {
  margin-top: 0px;
  color: #007bff;
  font-size: large;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 5ch;
}

.button-container{
  margin-left: 15px;
  font-size: x-large;
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

.url-container {
  display: flex;
  align-items: center;
  margin-left: 5px;
}

.url-subsection {
  font-size: small;
  color: #777;
  margin-right: 5px;
  display: inline-block;
}

</style>
