<template>
    <q-page class="q-pa-md q-gutter-sm">
        <div class="row q-mb-md">
            <div class="col-12">
                <div class="text-h5">Mi Espacio</div>
                <div class="text-subtitle2 text-grey-7">Visualiza los documentos asignados a tu cuenta</div>
            </div>
        </div>

        <q-inner-loading :showing="visible">
            <q-spinner-pie color="primary" size="70px" />
        </q-inner-loading>

        <div v-if="!visible && usuariosConAsignaciones.length > 0" class="row q-mb-md">
            <div class="col-12 col-md-6">
                <q-input
                    outlined
                    dense
                    v-model="searchTerm"
                    debounce="250"
                    label="Buscar usuario, carpeta o documento"
                    clearable
                    clear-icon="close"
                >
                    <template v-slot:append>
                        <q-icon name="search" />
                    </template>
                </q-input>
            </div>
        </div>

        <div v-if="!visible && filteredUsuariosConAsignaciones.length > 0">
            <q-expansion-item
                v-for="grupo in filteredUsuariosConAsignaciones"
                :key="grupo.usuario.uuid"
                :label="`${grupo.usuario.nombre || grupo.usuario.username} (${grupo.folders.length} carpetas)`"
                :caption="grupo.usuario.email || 'Sin correo registrado'"
                :header-class="'bg-primary text-white'"
                class="q-mb-md"
            >
                <q-expansion-item
                    v-for="carpeta in grupo.folders"
                    :key="carpeta.uuid"
                    :label="`${carpeta.nombre} (${carpeta.documents.length})`"
                    :caption="carpeta.ingreso_nombre ? `Ingreso: ${carpeta.ingreso_nombre}` : ''"
                    expand-separator
                    class="q-mb-sm bg-grey-1"
                >
                    <q-list bordered separator>
                        <q-item
                            v-for="documento in carpeta.documents"
                            :key="documento.uuid"
                        >
                            <q-item-section>
                                <q-item-label>{{ documento.nombre_original }}</q-item-label>
                                <q-item-label caption>{{ formatDate(documento.created) }}</q-item-label>
                            </q-item-section>
                            <q-item-section side top>
                                <div class="text-grey-8 q-gutter-xs">
                                    <q-btn
                                        size="sm"
                                        flat
                                        dense
                                        round
                                        icon="visibility"
                                        color="primary"
                                        @click="verDocumento(documento)"
                                        title="Ver documento"
                                    />
                                    <q-btn
                                        size="sm"
                                        flat
                                        dense
                                        round
                                        icon="download"
                                        color="positive"
                                        @click="descargarDocumento(documento)"
                                        title="Descargar documento"
                                    />
                                </div>
                            </q-item-section>
                        </q-item>
                    </q-list>
                </q-expansion-item>
            </q-expansion-item>
        </div>

        <div v-if="!visible && filteredUsuariosConAsignaciones.length === 0" class="row">
            <div class="col-12">
                <q-banner class="bg-info text-white">
                    <template v-slot:avatar>
                        <q-icon name="info" />
                    </template>
                    {{ noDocumentsMessage }}
                </q-banner>
            </div>
        </div>

        <!-- Dialog para previsualizar documento -->
        <q-dialog v-model="dialogPreview" full-width>
            <q-card>
                <q-card-section class="row items-center">
                    <div class="text-h6">{{ documentoSeleccionado?.nombre_original }}</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-none">
                    <iframe
                        v-if="documentoSeleccionado?.archivo"
                        :src="documentoSeleccionado.archivo"
                        style="width: 100%; height: 600px; border: none;"
                    />
                </q-card-section>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { Notify } from 'quasar'

const auth = useAuthStore()
const visible = ref(false)
const usuariosConAsignaciones = ref([])
const dialogPreview = ref(false)
const documentoSeleccionado = ref(null)
const searchTerm = ref('')

const filteredUsuariosConAsignaciones = computed(() => {
    const term = searchTerm.value.trim().toLowerCase()
    if (!term) {
        return usuariosConAsignaciones.value
    }

    return usuariosConAsignaciones.value
        .map((group) => {
            const matchingFolders = group.folders
                .map((folder) => {
                    const matchingDocuments = folder.documents.filter((doc) => {
                        return [doc.nombre_original]
                            .filter(Boolean)
                            .some((value) => value.toLowerCase().includes(term))
                    })

                    const folderMatches = [folder.nombre, folder.ingreso_nombre]
                        .filter(Boolean)
                        .some((value) => value.toLowerCase().includes(term))

                    if (matchingDocuments.length > 0 || folderMatches) {
                        return {
                            ...folder,
                            documents: matchingDocuments.length > 0 ? matchingDocuments : folder.documents,
                        }
                    }
                    return null
                })
                .filter(Boolean)

            const userMatches = [group.usuario.nombre, group.usuario.username, group.usuario.email]
                .filter(Boolean)
                .some((value) => value.toLowerCase().includes(term))

            if (userMatches || matchingFolders.length > 0) {
                return {
                    ...group,
                    folders: matchingFolders.length > 0 ? matchingFolders : group.folders,
                }
            }
            return null
        })
        .filter(Boolean)
})

const noDocumentsMessage = computed(() => {
    if (auth.isAdmin) {
        return 'No hay asignaciones de carpetas o documentos para ningún usuario.'
    }
    return 'No tienes documentos asignados. Contacta con el administrador para que te asigne documentos.'
})

onMounted(() => {
    loadDocumentosUsuario()
})

watch(dialogPreview, (val) => {
    if (!val && documentoSeleccionado.value && documentoSeleccionado.value.archivo && documentoSeleccionado.value.archivo.startsWith && documentoSeleccionado.value.archivo.startsWith('blob:')) {
        try { window.URL.revokeObjectURL(documentoSeleccionado.value.archivo) } catch (e) { /* ignore */ }
        documentoSeleccionado.value = null
    }
})

function normalizeResponseData(response) {
    if (Array.isArray(response.data)) {
        return response.data
    }
    if (response.data && Array.isArray(response.data.results)) {
        return response.data.results
    }
    return []
}

async function loadDocumentosUsuario() {
    visible.value = true
    usuariosConAsignaciones.value = []

    try {
        if (auth.isAdmin) {
            try {
                const response = await api.get('core/documents/user-folders-by-user/')
                usuariosConAsignaciones.value = normalizeResponseData(response)
                return
            } catch (adminError) {
                console.warn('Admin fallback to user-folders:', adminError)
            }
        }

        const response = await api.get('core/documents/user-folders/')
        const folders = normalizeResponseData(response)
        usuariosConAsignaciones.value = [{
            usuario: {
                uuid: auth.isAdmin ? 'todos' : 'self',
                nombre: auth.isAdmin ? 'Todos los documentos' : 'Mi Espacio',
                username: '',
                email: '',
            },
            folders,
        }]
    } catch (error) {
        console.error('Error al cargar documentos:', error)
        Notify.create({
            type: 'negative',
            message: 'Error al cargar tus documentos'
        })
    } finally {
        visible.value = false
    }
}

async function verDocumento(documento) {
    try {
        const response = await api.get(`core/documents/${documento.uuid}/download/?inline=1`, { responseType: 'blob' })
        const contentType = response.headers['content-type'] || 'application/octet-stream'
        const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }))
        documentoSeleccionado.value = { ...documento, archivo: url }
        dialogPreview.value = true
    } catch (error) {
        console.error('Error al previsualizar:', error)
        Notify.create({ type: 'negative', message: 'No se pudo previsualizar el documento' })
    }
}

async function descargarDocumento(documento) {
    try {
        const response = await api.get(`core/documents/${documento.uuid}/download/`, {
            responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', documento.nombre_original || 'documento')
        document.body.appendChild(link)
        link.click()
        link.parentNode.removeChild(link)
        window.URL.revokeObjectURL(url)
        Notify.create({
            type: 'positive',
            message: 'Documento descargado correctamente'
        })
    } catch (error) {
        console.error('Error al descargar:', error)
        Notify.create({
            type: 'negative',
            message: 'Error al descargar el documento'
        })
    }
}

function formatDate(value) {
    if (!value) return ''
    const date = new Date(value)
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
    })
}
</script>
