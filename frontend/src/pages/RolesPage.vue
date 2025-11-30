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
                        title="Roles" :filter="filter" row-key="name" >
                        

                        <template v-slot:top-left>
                            <Can I="create" an="Roles">
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
                                <q-td key="codigo" :props="props">
                                    {{ props.row.codigo }}
                                </q-td>

                                <q-td key="descripcion" :props="props">
                                    {{ props.row.descripcion }}
                                </q-td>

                                <q-td key="permisos" :props="props">
                                    <q-chip size="sm" v-for="permiso in props.row.permisos" :key="permiso.uuid" color="primary" text-color="white">
                                        {{ permiso.permiso.accion.descripcion }}
                                    </q-chip>
                                </q-td>

                                <Can I="update" an="Roles">
                                    <q-td key="edit" :props="props">
                                        <q-btn round size="xs" color="primary" icon="border_color"
                                            v-on:click="editing(props.row)" />
                                    </q-td>
                                </Can>

                                <Can I="delete" an="Roles">
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
            <q-card style="width: 800px; max-width: 80vw;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Rol</div>
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
                                <q-input filled v-model="codigo" label="Código *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="descripcion" label="Descripción *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        
                        <div class="row q-mt-md">
                            <div class="col-12">
                                <q-field label="Permisos" outlined filled>
                                    <template v-slot:default>
                                        <div class="q-pa-md bg-grey-2">
                                            <div class="row q-gutter-md">
                                                <q-checkbox
                                                    v-for="permiso in permisosDisponibles"
                                                    :key="permiso.uuid"
                                                    :model-value="permisosSeleccionados.includes(permiso.uuid)"
                                                    @update:model-value="togglePermiso(permiso.uuid)"
                                                    :label="`${permiso.accion.descripcion} - ${permiso.sujeto.descripcion}`"
                                                />
                                            </div>
                                        </div>
                                    </template>
                                </q-field>
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

    </q-page>
</template>

<style lang="scss"></style>

<script setup>
// Importacion de librerias
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { ability } from 'src/services/ability'
import { useAuthStore } from 'src/stores/auth'
import Swal from 'sweetalert2'

// Constantes
const path = 'seguridad/roles/'
const auth = useAuthStore()

// Declaracion de variables
const toolbar = ref(false)
const uuid = ref(null)
const codigo = ref(null)
const descripcion = ref(null)
const permisosDisponibles = ref([])
const permisosSeleccionados = ref([])
const columns = ref([
    { name: 'codigo', align: 'center', label: 'Código', field: 'codigo', sortable: true },
    { name: 'descripcion', align: 'center', label: 'Descripción', field: 'descripcion', sortable: true },
    { name: 'permisos', align: 'center', label: 'Permisos', field: 'permisos', sortable: false }
])
const data = ref([])
const filter = ref(null)
const isEditing = ref(false)
const visible = ref(false)
const form_ref = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })

onMounted(() => {
    loadTable()
    loadPermisos()
    setColumns()
    if (auth.rol === 'AD') {
        ability.update([
            { action: 'manage', subject: 'all' }
        ])
    }
})

// Funciones
async function loadPermisos() {
    try {
        const response = await api.get('seguridad/permisos/')
        permisosDisponibles.value = response.data
    } catch (error) {
        console.error('Error al cargar permisos:', error)
    }
}

function setColumns() {
    if (ability.can('update', 'Roles')) {
        columns.value.push({ name: 'edit', align: 'center', label: 'Editar', field: 'edit', sortable: true })
    }
    if (ability.can('delete', 'Roles')) {
        columns.value.push({ name: 'delete', align: 'center', label: 'Eliminar', field: 'delete', sortable: true })
    }
}

function togglePermiso(permisoUuid) {
    const index = permisosSeleccionados.value.indexOf(permisoUuid)
    if (index > -1) {
        permisosSeleccionados.value.splice(index, 1)
    } else {
        permisosSeleccionados.value.push(permisoUuid)
    }
}

async function onSubmit() {
    const success = await form_ref.value.validate()
    if (!success) return

    try {
        const nuevoRol = await api.post(path, {
            codigo: codigo.value,
            descripcion: descripcion.value
        })
        
        // Agregar permisos al rol
        for (const permisoUuid of permisosSeleccionados.value) {
            await api.post(`${path}${nuevoRol.data.uuid}/permisos/`, {
                permiso_uuid: permisoUuid
            })
        }
        
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al guardar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo guardar el rol. Por favor, inténtelo de nuevo.",
            icon: "error"
        })
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

    try {
        await api.put(path + uuid.value + '/', {
            codigo: codigo.value,
            descripcion: descripcion.value
        })
        
        // Sincronizar permisos
        const roActual = data.value.find(r => r.uuid === uuid.value)
        const permisosActuales = roActual.permisos.map(p => p.permiso.uuid)
        
        // Remover permisos que se deseleccionaron
        for (const permisoUuid of permisosActuales) {
            if (!permisosSeleccionados.value.includes(permisoUuid)) {
                await api.delete(`${path}${uuid.value}/permisos/${permisoUuid}/`)
            }
        }
        
        // Agregar nuevos permisos
        for (const permisoUuid of permisosSeleccionados.value) {
            if (!permisosActuales.includes(permisoUuid)) {
                await api.post(`${path}${uuid.value}/permisos/`, {
                    permiso_uuid: permisoUuid
                })
            }
        }
        
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al editar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo actualizar el rol. Por favor, inténtelo de nuevo.",
            icon: "error"
        })
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
          text: "El rol ha sido eliminado correctamente.",
          icon: "success"
        });
        
        loadTable();
      } catch (apiError) {
        Swal.fire({
          title: "Error",
          text: "No se pudo eliminar el rol. Por favor, inténtelo de nuevo.",
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
    codigo.value = null
    descripcion.value = null
    permisosSeleccionados.value = []
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
    codigo.value = row.codigo
    descripcion.value = row.descripcion
    permisosSeleccionados.value = row.permisos.map(p => p.permiso.uuid)
    toolbar.value = true
}
</script>
