import { defineStore } from "pinia"
import { ref, computed } from 'vue'
import { api } from 'boot/axios'

export const useAuthStore = defineStore('auth', () => {

  const token = ref(localStorage.getItem('auth_token') || null)
  const rol = ref(localStorage.getItem('rol') || null)
  const permisos = ref(JSON.parse(localStorage.getItem('permisos') || 'null') || [])

  if (token.value) {
    api.defaults.headers.common.Authorization = `JWT ${token.value}`
  }

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => rol.value === 'AD')

  async function login(payload) {
    const { data } = await api.post('seguridad/login/', payload)
    token.value = data.token
    rol.value = data.usuario.rol.codigo
    // Intentar capturar permisos si el backend los devuelve dentro del objeto usuario
    permisos.value = data.usuario.permisos || []
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('rol', data.usuario.rol.codigo)
    localStorage.setItem('permisos', JSON.stringify(permisos.value))
    api.defaults.headers.common.Authorization = `JWT ${data.token}`
    return true
  }

  function logout() {
    token.value = null
    rol.value = null
    permisos.value = []
    localStorage.removeItem('auth_token')
    localStorage.removeItem('rol')
    localStorage.removeItem('permisos')
    delete api.defaults.headers.common.Authorization
  }

  return {
    token,
    rol,
    permisos,
    isLoggedIn,
    isAdmin,
    login,
    logout
  }
})
