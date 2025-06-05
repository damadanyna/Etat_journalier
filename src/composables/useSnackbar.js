import { reactive } from 'vue'

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 2000,
})

export function useSnackbar() {
  return {
    snackbar,
    showSnackbar({ text, color = 'success', timeout = 2000 }) {
      snackbar.text = text
      snackbar.color = color
      snackbar.timeout = timeout
      snackbar.show = true
    },
  }
}
