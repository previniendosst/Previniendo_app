<template>
    <q-page class="q-pa-md q-gutter-sm">
        <div>
            <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
                <div>
                    <q-space />
                    <q-table dense :rows="data" :columns="columns" :loading="visible"
                        :loading-label="visible ? 'Cargando...' : ''" rows-per-page-label="Filas por página"
                        :no-data-label="visible ? 'No hay datos' : ''"
                        :no-results-label="visible ? 'No hay resultados' : ''"
                        :rows-per-page-options="[10, 15, 20, 25, 50, 0]" v-model:pagination="pagination"
                        title="Usuarios" :filter="filter" row-key="name" >
                        

                        <!-- problema de permiso: (Solucionado-> dentro de una etiqueta template se debia indicar donde renderizar el componente) --> 
                        <template v-slot:top-left>
                            <Can I="create" an="Usuarios">
                                <q-btn unelevated rounded icon="add" color="primary" @click="creating"
                                    label="Agregar" />
                                <q-space />
                            </Can>
                        </template>

                        <template v-slot:top-right>
                            <q-input dense debounce="300" v-model="filter" placeholder="Buscar">
                                <template v-slot:append>
                                    <q-icon name="search" />
                                </template>
                            </q-input>
                        </template>

                        <template v-slot:body="props">
                            <q-tr :props="props">
                                <q-td key="username" :props="props">
                                    {{ props.row.username }}
                                </q-td>

                                <q-td key="first_name" :props="props">
                                    {{ props.row.first_name }}
                                </q-td>

                                <q-td key="last_name" :props="props">
                                    {{ props.row.last_name }}
                                </q-td>

                                <q-td key="email" :props="props">
                                    {{ props.row.email }}
                                </q-td>

                                <q-td v-if="props.row.rol" key="rol" :props="props">
                                    {{ props.row.rol.descripcion }}
                                </q-td>

                                <q-td v-else key="rol-vacio" :props="props">
                                </q-td> <!--  (Comprobar que no se necesita y luego eliminar)-->

                                <q-td key="acciones" :props="props" style="width: 120px;">
                                    <div style="display: flex; align-items: center; gap: 4px; justify-content: center;">
                                        <Can I="update" an="Usuarios">
                                            <q-btn round size="xs" color="primary" icon="border_color" @click.stop="editing(props.row)" />
                                        </Can>
                                        <Can I="delete" an="Usuarios">
                                            <q-btn round size="xs" color="negative" icon="delete_forever" @click.stop="onDelete(props.row)" />
                                        </Can>
                                    </div>
                                </q-td>
                            </q-tr>
                        </template>
                    </q-table>
                </div>
            </transition>

            <q-inner-loading :showing="visible">
                <q-spinner-pie color="primary" size="70px" />
            </q-inner-loading>
        </div>

        <q-dialog v-model="toolbar" persistent>
            <q-card style="width: 700px; max-width: 80vw; max-height: 85vh; display: flex; flex-direction: column;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Usuario</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-banner class="bg-grey-3">
                    <template v-slot:avatar>
                        <q-icon name="warning" color="warning" />
                    </template>
                    Los campos marcados con (*) son obligatorios
                </q-banner>

                <q-card-section class="col overflow-auto">
                    <q-form ref="form_ref" @submit.prevent="onSubmit">
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-input filled v-model="username" label="Usuario *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="first_name" label="Nombres *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-input filled v-model="last_name" label="Apellidos *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="email" label="Correo electrónico *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-select
                                    filled
                                    v-model="rolSistema"
                                    label="Rol del Sistema"
                                    :options="optionsRoles"
                                    option-value="uuid"
                                    option-label="descripcion"
                                    clearable
                                    :loading="loadingRoles"
                                />
                            </div>
                            <div class="col-md-5">
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-11">
                                <div class="text-subtitle2 q-mb-md">Ingresos Asignados</div>
                                <div class="q-gutter-sm q-pa-sm" style="border: 1px solid #e0e0e0; border-radius: 4px;">
                                    <div class="row items-start q-gutter-sm">
                                        <div class="col">
                                            <q-chip
                                                v-for="ingreso in ingresosSeleccionados"
                                                :key="ingreso.uuid"
                                                removable
                                                @remove="removerIngreso(ingreso.uuid)"
                                                color="primary"
                                                text-color="white"
                                            >
                                                {{ ingreso.nombre }}
                                            </q-chip>
                                            <div v-if="ingresosSeleccionados.length === 0" class="text-grey-6 text-caption">No hay ingresos asignados</div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <q-btn
                                            size="sm"
                                            color="primary"
                                            icon="add"
                                            label="Agregar Ingreso"
                                            @click="mostrarDialogoIngresos"
                                            flat
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </q-form>
                </q-card-section>

                <q-separator />

                <q-card-actions class="row justify-between">
                    <div>
                        <q-btn v-if="isEditing" label="Enviar contraseña" @click.prevent="onSendPassword" color="info" />
                    </div>
                    <div class="q-gutter-sm">
                        <q-btn v-if="!isEditing" label="Guardar" @click.prevent="onSubmit" color="primary" />
                        <q-btn v-else label="Actualizar" @click.prevent="onEdit" color="primary" />
                        <q-btn label="Cancelar" v-close-popup color="negative" />
                    </div>
                </q-card-actions>

            </q-card>
        </q-dialog>

        <q-dialog v-model="dialogIngresos" persistent>
            <q-card style="width: 600px; max-width: 80vw;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Seleccionar Ingreso</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-card-section>
                    <div class="q-mb-md">
                        <q-input
                            outlined
                            v-model="busquedaIngresos"
                            label="Buscar ingresos..."
                            debounce="300"
                        >
                            <template v-slot:prepend>
                                <q-icon name="search" />
                            </template>
                        </q-input>
                    </div>

                    <q-list bordered separator>
                        <q-item
                            v-for="ingreso in ingresosDisponiblesFiltrados"
                            :key="ingreso.uuid"
                            clickable
                            @click="agregarIngreso(ingreso)"
                        >
                            <q-item-section>
                                <q-item-label>{{ ingreso.nombre }}</q-item-label>
                                <q-item-label caption>{{ ingreso.tipo_ingreso.descripcion }} - {{ ingreso.nit }}</q-item-label>
                            </q-item-section>
                        </q-item>
                        <q-item v-if="ingresosDisponiblesFiltrados.length === 0">
                            <q-item-section>
                                <q-item-label caption class="text-center text-grey-6">No hay ingresos disponibles</q-item-label>
                            </q-item-section>
                        </q-item>
                    </q-list>
                </q-card-section>

                <q-card-section class="bg-grey-1 q-pa-md">
                    <div class="text-subtitle2 q-mb-md">Crear nuevo ingreso</div>
                    <q-btn
                        size="sm"
                        color="primary"
                        icon="add"
                        label="Crear Ingreso"
                        @click="mostrarDialogoCrearIngreso"
                        flat
                    />
                </q-card-section>

                <q-card-actions align="right">
                    <q-btn label="Cancelar" v-close-popup color="negative" />
                </q-card-actions>
            </q-card>
        </q-dialog>

        <q-dialog v-model="dialogCrearIngreso" persistent>
            <q-card style="width: 500px; max-width: 80vw;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Crear Ingreso</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-card-section>
                    <q-form ref="formCrearIngreso" @submit.prevent="onCrearIngreso">
                        <div class="q-gutter-md">
                            <q-select
                                outlined
                                v-model="nuevoIngreso.tipo"
                                label="Tipo de Ingreso *"
                                :options="tiposIngresoOptions"
                                emit-value
                                map-options
                                option-value="value"
                                option-label="label"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.nombre"
                                label="Nombre *"
                                lazy-rules
                                :rules="[val => val && val.length > 0 || 'El campo es obligatorio']"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.nit"
                                label="NIT *"
                                lazy-rules
                                :rules="[val => val && val.length > 0 || 'El campo es obligatorio']"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.direccion"
                                label="Dirección"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.nombre_admin"
                                label="Nombre Representante Legal"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.correo"
                                label="Correo"
                                type="email"
                            />

                            <q-input
                                outlined
                                v-model="nuevoIngreso.telefono"
                                label="Teléfono"
                            />
                        </div>

                        <q-card-actions align="right" class="q-mt-md">
                            <q-btn label="Cancelar" v-close-popup color="negative" />
                            <q-btn label="Crear" type="submit" color="primary" :loading="loadingCrearIngreso" />
                        </q-card-actions>
                    </q-form>
                </q-card-section>
            </q-card>
        </q-dialog>

    </q-page>
</template>

<style lang="scss">
// CSS globalizado en app.scss
</style>

<script setup>
// Importacion de librerias
import { ref, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import { ability } from 'src/services/ability'
// import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

// Constantes
const path = 'seguridad/usuarios/'
//const $q = useQuasar()
const auth = useAuthStore()
import Swal from 'sweetalert2'

// Declaracion de variables
const toolbar = ref(false)
const dialogIngresos = ref(false)
const dialogCrearIngreso = ref(false)
const uuid = ref(null)
const username = ref(null)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)
const rolSistema = ref(null)
const optionsRoles = ref([])
const filterOptionsRoles = ref([])
const rol = ref(null)
const ingresosSeleccionados = ref([])
const ingresosDisponibles = ref([])
const busquedaIngresos = ref('')
const tiposIngresoOptions = ref([
    { label: 'Conjunto', value: 'conjunto' },
    { label: 'Empresa', value: 'empresa' }
])
const nuevoIngreso = ref({
    tipo: 'conjunto',  // Inicializar con valor por defecto válido
    nombre: null,
    nit: null,
    direccion: null,
    nombre_admin: null,
    correo: null,
    telefono: null
})
const loadingCrearIngreso = ref(false)
const formCrearIngreso = ref(null)
const columns = ref([
    { name: 'username', align: 'center', label: 'Usuario', field: 'username', sortable: true },
    { name: 'first_name', align: 'center', label: 'Nombres', field: 'first_name', sortable: true },
    { name: 'last_name', align: 'center', label: 'Apellidos', field: 'last_name', sortable: true },
    { name: 'email', align: 'center', label: 'Correo electrónico', field: 'email', sortable: true },
    { name: 'rol', align: 'center', label: 'Rol', field: 'rol', sortable: true },
    { name: 'acciones', align: 'center', label: 'Acciones', field: 'acciones', sortable: false }
])
const data = ref([])
const filter = ref(null)
const isEditing = ref(false)
const visible = ref(false)
// const confirm = ref(false)
const form_ref = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })
const loadingRoles = ref(false) // Loading para el select de roles
const loadingOnSubmit = ref(false) // Loading para el submit del formulario
const carpetasAsignadas = ref([])
const carpetasDisponibles = ref([])
const busquedaDocumentos = ref('')
const dialogDocumentos = ref(false)

onMounted(() => {
    loadTable()
    loadSelectRoles()
    loadIngresosDisponibles()
    if (auth.rol === 'AD') {
        ability.update([
            { action: 'manage', subject: 'all' }
        ])
    }
})

// Funciones
async function loadSelectRoles() {
    loadingRoles.value = true
    
    try {
        // El endpoint real de roles está en 'seguridad/roles/' (no bajo 'seguridad/usuarios/')
        const response = await api.get('seguridad/roles/')
        // Asegurarnos de que las opciones vienen con 'uuid' y 'descripcion'
        let rolesObtenidos = Array.isArray(response.data) ? response.data : (response.data.results || response.data || [])
        
        // Verificar si existe el rol AD, si no, agregarlo manualmente para que sea seleccionable
        const tieneAD = rolesObtenidos.find(r => r.codigo === 'AD')
        if (!tieneAD) {
            // Crear un rol AD virtual (sin guardar en DB) para que sea seleccionable
            rolesObtenidos.unshift({
                uuid: 'AD_ROLE',
                codigo: 'AD',
                descripcion: 'Administrador'
            })
        }
        
        optionsRoles.value = rolesObtenidos || []
        filterOptionsRoles.value = optionsRoles.value
    } catch (error) {
        console.error('Error al cargar roles:', error)
    } finally {
        loadingRoles.value = false
    }
}

// Las columnas de acciones están en `acciones` y los botones se muestran condicionalmente desde el template

function filterFnRoles(val, update) {
    if (val === '') {
        update(() => {
            filterOptionsRoles.value = optionsRoles.value
        })
        return
    }
    update(() => {
        const needle = val.toLowerCase()
        filterOptionsRoles.value = optionsRoles.value.filter(v => v.descripcion.toLowerCase().indexOf(needle) > -1)
    })
}

async function onSubmit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    try {
        // Extraer rol_sistema correctamente
        let rolSistemaValue = null
        if (rolSistema.value) {
            if (typeof rolSistema.value === 'string') {
                rolSistemaValue = rolSistema.value
            } else if (typeof rolSistema.value === 'object' && rolSistema.value.uuid) {
                rolSistemaValue = rolSistema.value.uuid
            }
        }
        
        const payload = {
            username: username.value,
            first_name: first_name.value,
            last_name: last_name.value,
            email: email.value,
            rol_sistema: rolSistemaValue,
            ingresos: ingresosSeleccionados.value.map(i => i.uuid)
        }
        console.log('Datos que se envían:', JSON.stringify(payload, null, 2))
        console.log('rolSistema value:', rolSistema.value)
        console.log('rolSistemaValue extraído:', rolSistemaValue)
        
        await api.post(path, payload)
        
        // Cerrar el diálogo INMEDIATAMENTE
        toolbar.value = false
        
        // Mostrar la alerta sin esperar (permitir que se cierre en paralelo)
        Swal.fire({
            title: "¡Éxito!",
            text: "Usuario creado correctamente",
            icon: "success"
        }).then(() => {
            loadTable()
        })
    } catch (error) {
        console.error('Error al guardar:', error)
        let errorMsg = "No se pudo guardar el usuario. Por favor, inténtelo de nuevo."
        
        if (error.response && error.response.data) {
            const errorData = error.response.data
            if (typeof errorData === 'object') {
                const firstKey = Object.keys(errorData)[0]
                const firstError = errorData[firstKey]
                if (Array.isArray(firstError)) {
                    errorMsg = firstError[0]
                } else if (typeof firstError === 'string') {
                    errorMsg = firstError
                }
            }
        }
        
        await Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error"
        })
    } finally {
        loadingOnSubmit.value = false
    }
}

async function loadTable() {
    visible.value = true
    try {
        const response = await api.get(path)
        data.value = response.data
    } catch (error) {
        console.error('Error al cargar la tabla:', error)
    } finally {
        visible.value = false
    }
}

async function onEdit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    try {
        // Extraer rol_sistema correctamente
        let rolSistemaValue = null
        if (rolSistema.value) {
            if (typeof rolSistema.value === 'string') {
                rolSistemaValue = rolSistema.value
            } else if (typeof rolSistema.value === 'object' && rolSistema.value.uuid) {
                rolSistemaValue = rolSistema.value.uuid
            }
        }
        
        await api.put(path + uuid.value + '/', {
            username: username.value,
            first_name: first_name.value,
            last_name: last_name.value,
            email: email.value,
            rol_sistema: rolSistemaValue,
            ingresos: ingresosSeleccionados.value.map(i => i.uuid)
        })
        
        // Cerrar el diálogo INMEDIATAMENTE
        toolbar.value = false
        
        // Mostrar la alerta sin esperar (permitir que se cierre en paralelo)
        Swal.fire({
            title: "¡Éxito!",
            text: "Usuario actualizado correctamente",
            icon: "success"
        }).then(() => {
            loadTable()
        })
    } catch (error) {
        console.error('Error al editar:', error)
        let errorMsg = "No se pudo actualizar el usuario. Por favor, inténtelo de nuevo."
        
        if (error.response && error.response.data) {
            const errorData = error.response.data
            if (typeof errorData === 'object') {
                const firstKey = Object.keys(errorData)[0]
                const firstError = errorData[firstKey]
                if (Array.isArray(firstError)) {
                    errorMsg = firstError[0]
                } else if (typeof firstError === 'string') {
                    errorMsg = firstError
                }
            }
        }
        
        await Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error"
        })
    } finally {
        loadingOnSubmit.value = false
    }
}

async function onDelete(row) {
  try {
    const result = await Swal.fire({
      title: "¿Está seguro?",
      text: "No podrá revertir esta acción",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar"
    });

    if (result.isConfirmed) {
      try {
        // Intentar eliminar el registro
        await api.delete(path + row.uuid + '/');
        
        // Mostrar mensaje de éxito
        await Swal.fire({
          title: "¡Eliminado!",
          text: "El registro ha sido eliminado correctamente.",
          icon: "success"
        });
        
        // Recargar la tabla
        loadTable();
      } catch (apiError) {
        // Si hay un error en la API, mostrar mensaje de error
        Swal.fire({
          title: "Error",
          text: "No se pudo eliminar el registro. Por favor, inténtelo de nuevo.",
          icon: "error"
        });
        console.error('Error al eliminar:', apiError);
      }
    }
  } catch (error) {
    console.error('Error general en onDelete:', error);
  }
}


function onReset() {
    username.value = null
    first_name.value = null
    last_name.value = null
    email.value = null
    rolSistema.value = null
    rol.value = null
    ingresosSeleccionados.value = []
}

function creating() {
    onReset()
    isEditing.value = false
    toolbar.value = true
}

function editing(row) {
    // Cerrar cualquier otro diálogo abierto
    dialogIngresos.value = false
    dialogCrearIngreso.value = false
    
    onReset()
    isEditing.value = true
    uuid.value = row.uuid
    username.value = row.username
    first_name.value = row.first_name
    last_name.value = row.last_name
    email.value = row.email
    if (row.rol) {
        rolSistema.value = row.rol.uuid
    }
    if (row.ingresos && row.ingresos.length > 0) {
        ingresosSeleccionados.value = row.ingresos.map(ui => ui.ingreso || ui)
        console.log('Ingresos cargados:', ingresosSeleccionados.value)
    } else {
        ingresosSeleccionados.value = []
    }
    console.log('Abriendo modal de edición para usuario:', row.username)
    toolbar.value = true
}

async function onSendPassword() {
    try {
        await api.get('seguridad/usuarios/generar_clave/' + uuid.value + '/')
        
        await Swal.fire({
            title: "¡Éxito!",
            text: "Contraseña enviada correctamente al correo del usuario",
            icon: "success"
        })
        
        toolbar.value = false
    } catch (error) {
        console.error('Error al enviar contraseña:', error)
        
        let errorMsg = "No se pudo enviar la contraseña. Por favor, inténtelo de nuevo."
        
        if (error.response && error.response.data) {
            const errorData = error.response.data
            if (typeof errorData === 'object') {
                const firstKey = Object.keys(errorData)[0]
                const firstError = errorData[firstKey]
                if (Array.isArray(firstError)) {
                    errorMsg = firstError[0]
                } else if (typeof firstError === 'string') {
                    errorMsg = firstError
                }
            }
        }
        
        await Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error"
        })
    }
}

async function loadIngresosDisponibles() {
    try {
        const response = await api.get('core/ingresos/')
        ingresosDisponibles.value = response.data
    } catch (error) {
        console.error('Error al cargar ingresos:', error)
    }
}

async function asignarIngresosDialog(usuario) {
    uuid.value = usuario.uuid
    if (usuario.ingresos) {
        ingresosSeleccionados.value = usuario.ingresos.map(ui => ui.ingreso || ui)
    } else {
        ingresosSeleccionados.value = []
    }
    mostrarDialogoIngresos()
}

function mostrarDialogoIngresos() {
    busquedaIngresos.value = ''
    dialogIngresos.value = true
}

function mostrarDialogoCrearIngreso() {
    dialogIngresos.value = false
    dialogCrearIngreso.value = true
}

const ingresosDisponiblesFiltrados = computed(() => {
    return ingresosDisponibles.value.filter(ingreso => {
        const nombre = ingreso.nombre.toLowerCase()
        const nit = ingreso.nit.toLowerCase()
        const busqueda = busquedaIngresos.value.toLowerCase()
        return nombre.includes(busqueda) || nit.includes(busqueda)
    })
})

function agregarIngreso(ingreso) {
    const existe = ingresosSeleccionados.value.find(i => i.uuid === ingreso.uuid)
    if (!existe) {
        ingresosSeleccionados.value.push(ingreso)
        // Guardar inmediatamente en el backend
        guardarIngresoAsignado(ingreso)
    }
}

async function guardarIngresoAsignado(ingreso) {
    try {
        await api.post(`seguridad/usuarios/${uuid.value}/ingresos/`, {
            ingreso_uuid: ingreso.uuid
        })
        console.log('Ingreso asignado correctamente')
    } catch (error) {
        console.error('Error al asignar ingreso:', error)
        // Remover de la lista si falla
        const index = ingresosSeleccionados.value.findIndex(i => i.uuid === ingreso.uuid)
        if (index > -1) {
            ingresosSeleccionados.value.splice(index, 1)
        }
    }
}

function removerIngreso(ingresoUuid) {
    const index = ingresosSeleccionados.value.findIndex(i => i.uuid === ingresoUuid)
    if (index > -1) {
        ingresosSeleccionados.value.splice(index, 1)
        // Eliminar del backend
        eliminarIngresoAsignado(ingresoUuid)
    }
}

async function eliminarIngresoAsignado(ingresoUuid) {
    try {
        await api.delete(`seguridad/usuarios/${uuid.value}/ingresos/${ingresoUuid}/`)
        console.log('Ingreso desasignado correctamente')
        // Recargar tabla para reflejar los cambios
        loadTable()
    } catch (error) {
        console.error('Error al desasignar ingreso:', error)
    }
}

const carpetasDisponiblesFiltradas = computed(() => {
    return carpetasDisponibles.value.filter(carpeta => {
        const nombre = carpeta.nombre.toLowerCase()
        const busqueda = busquedaDocumentos.value.toLowerCase()
        return nombre.includes(busqueda)
    })
})

async function mostrarDialogoDocumentos() {
    try {
        if (!ingresosSeleccionados.value || ingresosSeleccionados.value.length === 0) {
            $q.notify({ type: 'warning', message: 'Seleccione al menos un ingreso antes de asignar carpetas' })
            return
        }

        // Solicitar carpetas por ingreso y agregarlas sin duplicados
        const promises = ingresosSeleccionados.value.map(i => api.get(`core/documents/folders/?ingreso_uuid=${i.uuid}`))
        const results = await Promise.all(promises)
        const todas = []
        for (const res of results) {
            const items = Array.isArray(res.data) ? res.data : res.data.results || []
            for (const it of items) {
                if (!todas.find(t => t.uuid === it.uuid)) {
                    todas.push(it)
                }
            }
        }

        carpetasDisponibles.value = todas.filter(carpeta => {
            return !carpetasAsignadas.value.find(c => c.uuid === carpeta.uuid)
        })
        busquedaDocumentos.value = ''
        dialogDocumentos.value = true
    } catch (error) {
        console.error('Error al cargar carpetas disponibles:', error)
        $q.notify({ type: 'negative', message: 'Error al cargar carpetas disponibles' })
    }
}

function agregarDocumento(carpeta) {
    const existe = carpetasAsignadas.value.find(c => c.uuid === carpeta.uuid)
    if (!existe) {
        carpetasAsignadas.value.push(carpeta)
    }
    dialogDocumentos.value = false
}

function removerDocumento(carpetaUuid) {
    const index = carpetasAsignadas.value.findIndex(c => c.uuid === carpetaUuid)
    if (index > -1) {
        carpetasAsignadas.value.splice(index, 1)
    }
}

async function loadUserDocumentAssignments(usuarioUuid) {
    try {
        const response = await api.get('core/documents/user-access/', {
            params: { usuario: usuarioUuid }
        })
        carpetasAsignadas.value = response.data.map(item => ({
            uuid: item.carpeta_info.uuid,
            nombre: item.carpeta_info.nombre,
            ingreso: item.carpeta_info.ingreso
        }))
    } catch (error) {
        console.error('Error al cargar documentos asignados:', error)
        carpetasAsignadas.value = []
    }
}

async function onCrearIngreso(e) {
    e.preventDefault()
    const success = await formCrearIngreso.value.validate()
    if (!success) {
        console.log('Validación fallida')
        return
    }

    loadingCrearIngreso.value = true

    try {
        // El tipo ya viene correcto gracias a emit-value + map-options
        const tipoValue = nuevoIngreso.value.tipo
        
        console.log('Creando ingreso con tipo:', tipoValue)
        
        const response = await api.post('core/ingresos/', {
            tipo_ingreso: tipoValue,
            nombre: nuevoIngreso.value.nombre,
            nit: nuevoIngreso.value.nit,
            direccion: nuevoIngreso.value.direccion,
            nombre_admin: nuevoIngreso.value.nombre_admin,
            correo: nuevoIngreso.value.correo,
            telefono: nuevoIngreso.value.telefono
        })

        // Agregar el nuevo ingreso a la lista disponible
        ingresosDisponibles.value.push(response.data)
        
        // Agregarlo a los seleccionados
        ingresosSeleccionados.value.push(response.data)

        // Resetear el formulario
        nuevoIngreso.value = {
            tipo: 'conjunto',  // Volver al valor por defecto
            nombre: null,
            nit: null,
            direccion: null,
            nombre_admin: null,
            correo: null,
            telefono: null
        }

        dialogCrearIngreso.value = false
        dialogIngresos.value = false

        await Swal.fire({
            title: "Éxito",
            text: "Ingreso creado y asignado correctamente",
            icon: "success",
            allowOutsideClick: false,
            allowEscapeKey: false
        })
    } catch (error) {
        console.error('Error al crear ingreso:', error)
        let errorMsg = "No se pudo crear el ingreso. Por favor, inténtelo de nuevo."
        
        if (error.response && error.response.data) {
            const errorData = error.response.data
            if (typeof errorData === 'object') {
                const firstKey = Object.keys(errorData)[0]
                const firstError = errorData[firstKey]
                if (Array.isArray(firstError)) {
                    errorMsg = firstError[0]
                } else if (typeof firstError === 'string') {
                    errorMsg = firstError
                }
            }
        }
        
        Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error"
        })
    } finally {
        loadingCrearIngreso.value = false
    }
}
</script>
