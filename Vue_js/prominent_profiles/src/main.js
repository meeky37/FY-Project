import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faExternalLinkAlt, faCircleChevronUp, faCircleChevronDown, faCircleMinus, faShuffle, faMagnifyingGlassChart, faPercent, faClock, faArrowUp, faArrowDown, faCalendarDays } from '@fortawesome/free-solid-svg-icons'
import { faGoogle } from '@fortawesome/free-brands-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { setupCalendar, Calendar, DatePicker } from 'v-calendar'
import 'v-calendar/style.css'

library.add(faExternalLinkAlt)
library.add(faCircleChevronUp)
library.add(faCircleChevronDown)
library.add(faCircleMinus)
library.add(faShuffle)
library.add(faMagnifyingGlassChart)
library.add(faPercent)
library.add(faClock)
library.add(faArrowUp)
library.add(faArrowDown)
library.add(faGoogle)
library.add(faCalendarDays)

const app = createApp(App).use(router)

app.mount('#app')
app.use(setupCalendar, {})
app.component('font-awesome-icon', FontAwesomeIcon)
app.component('VCalendar', Calendar)
app.component('VDatePicker', DatePicker)
