import { API_BASE_URL } from '@/config'

export const fetchMiniBingEntity = async function () {
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
    // Bing data may not be available, e.g., app_visible is false in the database or Bing API job not run yet.
    await this.fetchEntityName(id)
  }
}

export const fetchEntityName = async function (entityId) {
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
}

export const getMediaUrl = function (bingEntity) {
  // Extract description URL from contractual rules
  const mediaContract = bingEntity.contractual_rules.find(
    (rule) =>
      rule._type === 'ContractualRules/MediaAttribution' &&
      rule.targetPropertyName === 'image'
  )

  const mediaUrl = mediaContract ? mediaContract.url : null
  return mediaUrl
}

export const getAttributionMessage = function (bingEntity) {
  if (bingEntity && bingEntity.contractual_rules) {
    const mediaUrl = this.getMediaUrl(bingEntity)
    return `Attribution: ${mediaUrl}`
  } else {
    return 'Attribution: Not available'
  }
}

export const redirectToEntityPage = function (lastVisit) {
  // Check if lastVisit is an event object (Not from trending profile card)
  if (lastVisit instanceof Event) {
    lastVisit = undefined
  }

  let url = '/entity/' + this.entry.entity_id
  console.log('seen last visit')
  console.log(lastVisit)

  if (lastVisit) {
    url += '?last_visit=' + encodeURIComponent(lastVisit)
  }

  this.$router.push(url)
}

export const viewArticleDetail = function (articleID) {
  const articleId = articleID
  const entityId = this.entry.entity_id
  this.$router.push({ name: 'entryId', params: { entityId, articleId } })
}
