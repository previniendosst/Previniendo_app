import { defineStore } from "pinia"
import { ref, computed } from 'vue'
import { api } from 'boot/axios'

export const useAuthStore = defineStore('auth', () => {

  const token = ref(localStorage.getItem('auth_token') || null)
  const rol = ref(localStorage.getItem('rol') || null)

  if (token.value) {
    api.defaults.headers.common.Authorization = `JWT ${token.value}`
  }

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => rol.value === 'AD')

  async function login(payload) {
    const { data } = await api.post('seguridad/login/', payload)
    token.value = data.token
    rol.value = data.usuario.rol.codigo
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('rol', data.usuario.rol.codigo)
    api.defaults.headers.common.Authorization = `JWT ${data.token}`
    return true
  }

  function logout() {
    token.value = null
    rol.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('rol')
    delete api.defaults.headers.common.Authorization
  }

  return {
    token,
    rol,
    isLoggedIn,
    isAdmin,
    login,
    logout
  }
})
