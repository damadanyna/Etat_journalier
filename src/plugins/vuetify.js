import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'  

export default createVuetify({
  components,
  defaultTheme: 'dark',
  themes: {
    light: {
      dark: false,
      colors: {
        background: '#AAAAAA',
        surface: '#FFFFFF',
        primary: '#1976D2',
        // autres couleurs...
      },
    },
    dark: {
      dark: true,
      colors: {
        background: '#121212',
        surface: '#1E1E1E',
        primary: '#90CAF9',
        // autres couleurs...
      },
    },
  },
  directives,
  icons: {
    defaultSet: 'mdi',
  },
})
