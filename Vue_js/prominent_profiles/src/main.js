import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faExternalLinkAlt, faCircleChevronUp, faCircleChevronDown, faCircleMinus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faExternalLinkAlt)
library.add(faCircleChevronUp)
library.add(faCircleChevronDown)
library.add(faCircleMinus)

const app = createApp(App).use(router)

app.mount('#app')
app.component('font-awesome-icon', FontAwesomeIcon)
