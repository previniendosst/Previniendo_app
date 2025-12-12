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

        <div v-if="!visible && carpetasConDocumentos.length > 0">
            <q-expansion-item
                v-for="carpeta in carpetasConDocumentos"
                :key="carpeta.uuid"
                :icon="carpeta.expanded ? 'folder_open' : 'folder'"
                :label="`${carpeta.nombre} (${carpeta.documents.length})`"
                :header-class="'bg-primary text-white'"
                class="q-mb-md"
            >
                <q-list bordered separator>
                    <q-item
                        v-for="documento in carpeta.documents"
                        :key="documento.uuid"
                    >
                        <q-item-section>
                            <q-item-label>{{ documento.nombre_original }}</q-item-label>
                            <q-item-label caption>{{ documento.created | formatDate }}</q-item-label>
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
        </div>

        <div v-if="!visible && carpetasConDocumentos.length === 0" class="row">
            <div class="col-12">
                <q-banner class="bg-info text-white">
                    <template v-slot:avatar>
                        <q-icon name="info" />
                    </template>
                    No tienes documentos asignados. Contacta con el administrador para que te asigne documentos.
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
import { ref, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { Notify } from 'quasar'

const auth = useAuthStore()
const visible = ref(false)
const carpetasConDocumentos = ref([])
const dialogPreview = ref(false)
const documentoSeleccionado = ref(null)

onMounted(() => {
    loadDocumentosUsuario()
})

async function loadDocumentosUsuario() {
    visible.value = true
    try {
        const response = await api.get('core/documents/user-folders/')
        carpetasConDocumentos.value = response.data || []
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

function verDocumento(documento) {
    documentoSeleccionado.value = documento
    dialogPreview.value = true
}

async function descargarDocumento(documento) {
    try {
        const response = await api.get(`core/documents/${documento.uuid}/download/`, {
            responseType: 'blob'
        })
        
        // Crear URL de descarga
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
</script>
