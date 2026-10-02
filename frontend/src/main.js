import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import bidi from './directives/bidi'
import './styles/rtl.css'

const app = createApp(App)

app.use(router)
app.use(i18n)
app.directive('bidi', bidi)

app.mount('#app')
