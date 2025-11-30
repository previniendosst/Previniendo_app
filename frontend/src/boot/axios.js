import 'sweetalert2/dist/sweetalert2.min.css'
import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useAuthStore } from 'src/stores/auth'

// URL base de la API ()
const BASE_URL = (process.env.API || '').replace(/"/g, '')  // 'https://vtpwh5ln-8000.use2.devtunnels.ms/api/v1/' // 

// Crear instancia de Axios específica para tu API
const api = axios.create({ baseURL: BASE_URL })

export default defineBoot(({ app, router }) => {
  const auth = useAuthStore()

  // Interceptor de solicitudes: añade token JWT si existe
  api.interceptors.request.use(
    config => {
      const token = auth.token
      if (token) {
        config.headers.Authorization = `JWT ${token}`
      }
      return config
    },
    error => Promise.reject(error)
  )

  // Interceptor de respuestas: maneja SweetAlert y redirección
  api.interceptors.response.use(
    response => {
      // Mostrar SweetAlert de éxito para métodos que modifican datos,
      // excepto el login
      const métodosConNotificación = ['post', 'put', 'patch', 'delete']
      const url = response.config.url || ''

      if (
        métodosConNotificación.includes(response.config.method) &&
        !url.endsWith('/seguridad/login/')
      ) {
        Swal.fire({
          icon: 'success',
          title: 'Proceso exitoso',
          showConfirmButton: false,
          timer: 1500,
          customClass: { container: 'my-swal' }
        })
      }

      return response
    },

    error => {
      // Construir mensaje de error a partir de la respuesta
      const errores = error.response?.data
      let html = ''

      console.log('error', errores)

      if (errores && typeof errores === 'object') {
        Object.values(errores).forEach(msg => {
          if (!errores.existe) {
            html = error.response.data.detail || error.response.data.message
          }
          else {
            html += `<p>${msg}</p>`
          }
        })
      } else {
        html = '<p>Ocurrió un error inesperado.</p>'
      }

      // Mostrar SweetAlert de error
      Swal.fire({
        icon: 'error',
        //title: 'Error',
        html,
        showCloseButton: true,
        focusConfirm: false,
        confirmButtonText: 'Aceptar',
        confirmButtonColor: '#3085d6',
        customClass: { container: 'my-swal' }
      }).then(() => {
        // Si expira sesión, redirigir a login
        if (error.response?.status === 401) {
          auth.logout()
          router.push({ name: 'login' })
        }
      })

      return Promise.reject(error)
    }
  )

  // Exponer instancias en Vue Options API si es necesario
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }