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
                        title="Ingresos" :filter="filter" row-key="name" >
                        

                        <template v-slot:top-left>
                            <Can I="create" an="Ingresos">
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
                                <q-td key="tipo_ingreso" :props="props">
                                    {{ props.row.tipo_ingreso.descripcion }}
                                </q-td>

                                <q-td key="nombre" :props="props">
                                    {{ props.row.nombre }}
                                </q-td>

                                <q-td key="nit" :props="props">
                                    {{ props.row.nit }}
                                </q-td>

                                <q-td key="nombre_admin" :props="props">
                                    {{ props.row.nombre_admin }}
                                </q-td>

                                <q-td key="correo" :props="props">
                                    {{ props.row.correo }}
                                </q-td>

                                <q-td key="telefono" :props="props">
                                    {{ props.row.telefono }}
                                </q-td>

                                <Can I="update" an="Ingresos">
                                    <q-td key="edit" :props="props">
                                        <q-btn round size="xs" color="primary" icon="border_color"
                                            v-on:click="editing(props.row)" />
                                    </q-td>
                                </Can>

                                <q-td key="documents" :props="props">
                                    <q-btn round size="xs" color="secondary" icon="folder_open" label="Docs"
                                        v-on:click="openDocuments(props.row)" />
                                </q-td>

                                <Can I="delete" an="Ingresos">
                                    <q-td key="delete" :props="props">
                                        <q-btn round size="xs" color="negative" icon="delete_forever"
                                            v-on:click="onDelete(props.row)" />
                                    </q-td>
                                </Can>
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
            <q-card style="width: 700px; max-width: 80vw;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Ingreso</div>
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
                    <q-form ref="form_ref" @submit.prevent="onSubmit">
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-select use-input input-debounce="0" @filter="filterFnTipos" filled v-model="tipo_ingreso"
                                    :options="filterOptionsTipos" option-label="descripcion" option-value="codigo"
                                    label="Tipo Ingreso *" emit-value map-options lazy-rules
                                    :rules="[val => !!val || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="nombre" label="Nombre *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-input filled v-model="nit" label="NIT *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="telefono" label="Teléfono *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-11">
                                <q-input filled v-model="direccion" label="Dirección *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-11">
                                <q-input filled v-model="nombre_admin" label="Nombre Admin / Representante Legal *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-11">
                                <q-input filled v-model="correo" label="Correo electrónico *" type="email" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                    </q-form>
                </q-card-section>

                <div class="row justify-between">
                    <q-card-actions align="left" class="bg-white text-teal">
                    </q-card-actions>
                    <q-card-actions align="right" class="bg-white text-teal">
                        <q-btn v-if="!isEditing" label="Guardar" @click.prevent="onSubmit" color="primary" />
                        <q-btn v-else label="Actualizar" @click.prevent="onEdit" color="primary" />
                        <q-btn label="Cancelar" v-close-popup color="negative" />
                    </q-card-actions>
                </div>

            </q-card>
        </q-dialog>

        <DocumentsModal
          ref="docsModalRef"
          v-model:modelValue="showDocuments"
          :ingresoUuid="selectedIngresoUuid"
          @uploaded="onDocumentsUploaded"
        />    </q-page>
</template>

<style lang="scss"></style>

<script setup>
// Importacion de librerias
import { ref, onMounted } from 'vue'
import DocumentsModal from 'src/components/DocumentsModal.vue'
import { api } from 'src/boot/axios'
import { ability } from 'src/services/ability'
import { useAuthStore } from 'src/stores/auth'
import Swal from 'sweetalert2'

// Constantes
const path = 'core/ingresos/'
const auth = useAuthStore()

// Declaracion de variables
const toolbar = ref(false)
const uuid = ref(null)
const tipo_ingreso = ref(null)
const nombre = ref(null)
const nit = ref(null)
const direccion = ref(null)
const nombre_admin = ref(null)
const correo = ref(null)
const telefono = ref(null)
const optionsTipos = ref([])
const filterOptionsTipos = ref([])
const columns = ref([
    { name: 'tipo_ingreso', align: 'center', label: 'Tipo', field: 'tipo_ingreso', sortable: true },
    { name: 'nombre', align: 'center', label: 'Nombre', field: 'nombre', sortable: true },
    { name: 'nit', align: 'center', label: 'NIT', field: 'nit', sortable: true },
    { name: 'nombre_admin', align: 'center', label: 'Administrador', field: 'nombre_admin', sortable: true },
    { name: 'correo', align: 'center', label: 'Correo', field: 'correo', sortable: true },
    { name: 'telefono', align: 'center', label: 'Teléfono', field: 'telefono', sortable: true },
    { name: 'edit', align: 'center', label: 'Editar', field: 'edit', sortable: false },
    { name: 'documents', align: 'center', label: 'Documentos', field: 'documents', sortable: false },
    { name: 'delete', align: 'center', label: 'Eliminar', field: 'delete', sortable: false }
])
const data = ref([])
const filter = ref(null)
const isEditing = ref(false)
const visible = ref(false)
const form_ref = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })
const loadingOnSubmit = ref(false)
const showDocuments = ref(false)
const selectedIngresoUuid = ref(null)
const docsModalRef = ref(null)

onMounted(() => {
    loadTable()
    loadSelectTipos()
    setColumns()
    if (auth.rol === 'AD') {
        ability.update([
            { action: 'manage', subject: 'all' }
        ])
    }
})

// Funciones
async function loadSelectTipos() {
    try {
        const response = await api.get(path + 'tipos/')
        optionsTipos.value = response.data
        filterOptionsTipos.value = response.data
    } catch (error) {
        console.error('Error al cargar tipos:', error)
    }
}

function openDocuments(row) {
    selectedIngresoUuid.value = row.uuid
    // Llamar al método expuesto del modal para abrir y cargar carpetas
    if (docsModalRef.value && typeof docsModalRef.value.open === 'function') {
        docsModalRef.value.open(row.uuid)
    } else {
        // Fallback: usar v-model si el ref aún no está disponible
        showDocuments.value = true
    }
}

function onDocumentsUploaded() {
    // recargar tabla si es necesario
    loadTable()
}

function setColumns() {
    // Filtrar columnas según permisos
    if (!ability.can('update', 'Ingresos')) {
        columns.value = columns.value.filter(col => col.name !== 'edit')
    }
    if (!ability.can('delete', 'Ingresos')) {
        columns.value = columns.value.filter(col => col.name !== 'delete')
    }
}

function filterFnTipos(val, update) {
    if (val === '') {
        update(() => {
            filterOptionsTipos.value = optionsTipos.value
        })
        return
    }
    update(() => {
        const needle = val.toLowerCase()
        filterOptionsTipos.value = optionsTipos.value.filter(v => v.descripcion.toLowerCase().indexOf(needle) > -1)
    })
}

async function onSubmit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    try {
        await api.post(path, {
            tipo_ingreso: tipo_ingreso.value,
            nombre: nombre.value,
            nit: nit.value,
            direccion: direccion.value,
            nombre_admin: nombre_admin.value,
            correo: correo.value,
            telefono: telefono.value
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al guardar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo guardar el ingreso. Por favor, inténtelo de nuevo.",
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
        await api.put(path + uuid.value + '/', {
            tipo_ingreso: tipo_ingreso.value,
            nombre: nombre.value,
            nit: nit.value,
            direccion: direccion.value,
            nombre_admin: nombre_admin.value,
            correo: correo.value,
            telefono: telefono.value
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al editar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo actualizar el ingreso. Por favor, inténtelo de nuevo.",
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
        await api.delete(path + row.uuid + '/');
        
        await Swal.fire({
          title: "¡Eliminado!",
          text: "El registro ha sido eliminado correctamente.",
          icon: "success"
        });
        
        loadTable();
      } catch (apiError) {
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
    tipo_ingreso.value = null
    nombre.value = null
    nit.value = null
    direccion.value = null
    nombre_admin.value = null
    correo.value = null
    telefono.value = null
}

function creating() {
    onReset()
    isEditing.value = false
    toolbar.value = true
}

function editing(row) {
    onReset()
    isEditing.value = true
    uuid.value = row.uuid
    tipo_ingreso.value = row.tipo_ingreso.codigo
    nombre.value = row.nombre
    nit.value = row.nit
    direccion.value = row.direccion
    nombre_admin.value = row.nombre_admin
    correo.value = row.correo
    telefono.value = row.telefono
    toolbar.value = true
}
</script>
