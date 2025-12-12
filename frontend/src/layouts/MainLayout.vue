<template>
  <q-layout view="hHh lpR fFf">

    <q-header elevated class="bg-primary text-white ">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="left = !left" />

        <q-toolbar-title>
          Previniendo App
        </q-toolbar-title>
        <q-space />
        <div class="q-gutter-sm row items-center no-wrap">
          <q-btn dense flat>
            <q-menu auto-close>
              <q-list dense>
              </q-list>
            </q-menu>
          </q-btn>
          <q-btn-dropdown round flat icon="person">
            <div class="row no-wrap q-pa-md">
              <div class="column items-center">
                <q-avatar @click="editing" class="cursor" size="72px">
                  <img src="https://cdn.quasar.dev/img/boy-avatar.png">
                </q-avatar>
                <div @click="editing" class="text-subtitle1 q-mt-md q-mb-xs cursor">{{ full_name }}</div>
                <q-btn color="primary" label="Cerrar sesión" push size="sm" @click="logout" v-close-popup />
              </div>
            </div>
          </q-btn-dropdown>
        </div>
      </q-toolbar>
    </q-header>
    <q-drawer :width="200" show-if-above v-model="left" side="left" bordered class="bg-blue-grey-10 text-white">
      <q-list>
        <q-item clickable :to="{ name: 'index' }" exact v-ripple exact-active-class="text-white bg-primary">
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Inicio</q-item-label>
          </q-item-section>
        </q-item>

        <Can I="read" an="MiEspacio">
          <q-item clickable :to="{ name: 'mi-espacio' }" exact v-ripple exact-active-class="text-white bg-primary">
            <q-item-section avatar>
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Mi Espacio</q-item-label>
            </q-item-section>
          </q-item>
        </Can>

        <q-separator />

        <Can I="read" an="Usuarios">
          <q-item clickable :to="{ name: 'usuarios' }" exact v-ripple exact-active-class="text-white bg-primary">
            <q-item-section avatar>
              <q-icon name="person" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Usuarios</q-item-label>
            </q-item-section>
          </q-item>
        </Can>

        <Can I="read" an="Ingresos">
          <q-item clickable :to="{ name: 'ingresos' }" exact v-ripple exact-active-class="text-white bg-primary">
            <q-item-section avatar>
              <q-icon name="business" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Ingresos</q-item-label>
            </q-item-section>
          </q-item>
        </Can>

        <Can I="read" an="Roles">
          <q-item clickable :to="{ name: 'roles' }" exact v-ripple exact-active-class="text-white bg-primary">
            <q-item-section avatar>
              <q-icon name="security" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Roles</q-item-label>
            </q-item-section>
          </q-item>
        </Can>

      </q-list>
    </q-drawer>

    <q-dialog v-model="toolbar">
      <q-card style="width: 700px; max-width: 80vw;">

        <q-card-section class="row items-center">
          <div class="text-h6">Mi perfil</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-banner class="bg-grey-3">
          <template v-slot:avatar>
            <q-icon name="warning" color="warning" />
          </template>
          Los campos marcados con (*) son obligatorios
        </q-banner>

        <q-card-section>
          <q-form ref="form_ref">
            <div class="row justify-around">
              <div class="col-md-5">
                <q-input filled v-model="first_name" label="Nombres *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div class="col-md-5">
                <q-input filled v-model="last_name" label="Apellidos *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div class="col-md-11">
                <q-input autocomplete="off" filled v-model="email" label="Correo electrónico *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div v-if="nuevo_password" class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña *"
                  lazy-rules :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div v-else class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña" />
              </div>
              <div class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="nuevo_password"
                  label="Nueva contraseña *" />
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="bg-white text-teal">
          <q-btn label="Actualizar" @click.prevent="onEdit" color="primary" />
          <q-btn label="Cancelar" v-close-popup color="negative" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>

</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useRouter } from 'vue-router'
import { ability } from 'src/services/ability'

const auth = useAuthStore()
const router = useRouter()

// Constante de path para la API
const path = 'seguridad/perfil/'

const left = ref(false)
const toolbar = ref(false)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)
const actual_password = ref(null)
const nuevo_password = ref(null)
const full_name = ref('')
const form_ref = ref(null)

async function logout() {
  try {
    // Limpiar la ability ANTES de logout para evitar que queden reglas en caché
    ability.update([])
    auth.logout();
    router.push('/login');
  } catch (error) {
    console.error('Error al cerrar sesión', error);
  }
}

async function loadUser() {

  const response = await api.get(path)

  first_name.value = response.data.first_name
  last_name.value = response.data.last_name
  email.value = response.data.email
  full_name.value = first_name.value + ' ' + last_name.value
}



function editing() {

  toolbar.value = true
  actual_password.value = null
  nuevo_password.value = null
}

async function onEdit() {

  const success = await form_ref.value.validate()
  if (!success) return

  await api.put(path, {
    first_name: first_name.value,
    last_name: last_name.value,
    email: email.value,
    actual_password: actual_password.value,
    nuevo_password: nuevo_password.value
  })

  toolbar.value = false
  loadUser()
}

function setAbilities(rol) {
  // Asegurar que no existan reglas por defecto que sobreescriban las
  // que vienen del backend. Solo conceder "manage:all" para admin (AD).
  // Para cualquier otro rol, si no hay permisos cargados, limpiar las reglas.
  if (!rol) {
    ability.update([])
    return
  }

  if (rol === 'AD') {
    ability.update([
      { action: 'manage', subject: 'all' }
    ])
    return
  }

  // No forzar permisos por defecto aquí: LoginPage.vue se encarga de
  // construir las reglas a partir de `auth.permisos`. Si no hay permisos
  // en el store, limpamos las reglas para evitar permisos implícitos.
  if (!auth.permisos || auth.permisos.length === 0) {
    ability.update([])
  }
}

onMounted(() => {
  loadUser();
  setAbilities(auth.rol)
})

watch(() => auth.rol, rol => {
  setAbilities(rol)
})
</script>

<style lang="scss">
.cursor {
  cursor: pointer
}
</style>
