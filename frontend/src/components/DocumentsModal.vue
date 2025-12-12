<template>
  <q-dialog v-model="show" persistent>
    <q-card style="min-width: 750px; max-width: 95vw; border-radius: 12px;">
      <!-- Header -->
      <q-card-section class="bg-primary text-white row items-center q-pa-lg">
        <q-icon name="folder_open" size="md" class="q-mr-md" />
        <div>
          <div class="text-h6 q-mb-none">Gestión de Documentos</div>
          <div class="text-caption">Crea carpetas y carga tus archivos</div>
        </div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup @click="close" color="white" />
      </q-card-section>

      <!-- Main Content -->
      <q-card-section class="q-pa-lg">
        
        <!-- Sección 1: Nueva Carpeta (Solo Admin) -->
        <div v-if="isAdmin" class="q-mb-lg">
          <div class="text-subtitle1 text-weight-bold q-mb-md">
            <q-icon name="create_new_folder" color="primary" class="q-mr-sm" />
            Nueva Carpeta
          </div>
          <div class="row q-col-gutter-md items-end">
            <div class="col">
              <q-input 
                filled
                dense
                v-model="newFolderName" 
                label="Nombre de la carpeta"
                placeholder="ej: Documentos Importantes"
                outlined
              />
            </div>
            <div class="col-auto">
              <q-btn 
                label="Crear" 
                color="primary" 
                icon-right="add"
                unelevated
                padding="md lg"
                @click="onCreateFolder"
                :disable="!newFolderName.trim()"
              />
            </div>
          </div>
        </div>

        <q-separator v-if="isAdmin" class="q-my-lg" />

        <!-- Sección 2: Seleccionar Carpeta y Cargar Archivos (Solo Admin) -->
        <div v-if="isAdmin" class="q-mb-lg">
          <div class="text-subtitle1 text-weight-bold q-mb-md">
            <q-icon name="publish" color="primary" class="q-mr-sm" />
            Cargar Archivos
          </div>
          
          <div class="row q-col-gutter-lg">
            <!-- Selector de Carpeta -->
            <div class="col-12 col-md-5">
              <q-select
                filled
                dense
                v-model="selectedFolder"
                :options="foldersOptions"
                option-value="uuid"
                option-label="nombre"
                emit-value
                map-options
                @update:model-value="onFolderSelected"
                label="Selecciona una carpeta"
                :disable="folders.length === 0"
              />
              <q-item-label v-if="folders.length === 0" caption class="q-mt-sm text-warning">
                Crea una carpeta primero
              </q-item-label>
            </div>

            <!-- Uploader -->
            <div class="col-12 col-md-7">
              <div class="uploader-container bg-grey-2 rounded-borders q-pa-lg" style="border: 2px dashed #1976d2; min-height: 150px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                <q-uploader
                  url=""
                  :factory="uploaderFactory"
                  label="Arrastra archivos aquí o haz click"
                  multiple
                  ref="uploader"
                  :hide-upload-btn="true"
                  class="full-width"
                  max-file-size="52428800"
                />
              </div>
            </div>
          </div>
        </div>

        <q-separator v-if="isAdmin" class="q-my-lg" />

        <!-- Sección 3: Documentos Cargados -->
        <div v-if="documents.length > 0">
          <div class="text-subtitle1 text-weight-bold q-mb-md">
            <q-icon name="description" color="primary" class="q-mr-sm" />
            Documentos en la Carpeta ({{ documents.length }})
          </div>
          <q-table 
            :rows="documents" 
            :columns="docColumns" 
            row-key="uuid" 
            dense 
            flat
            card-class="no-shadow"
            :pagination.sync="tablePagination"
          >
            <template v-slot:body="props">
              <q-tr :props="props" class="hover-row">
                <q-td key="nombre" :props="props">
                  <div class="flex items-center">
                    <q-icon name="attachment" size="sm" color="grey-7" class="q-mr-sm" />
                    <span class="text-weight-500">{{ props.row.nombre_original || props.row.uuid }}</span>
                  </div>
                </q-td>
                <q-td key="fecha" :props="props">
                  <q-item-label caption>{{ formatDate(props.row.created) }}</q-item-label>
                </q-td>
                <q-td key="archivo" :props="props">
                  <div class="row q-gutter-sm">
                    <q-btn
                      size="sm"
                      flat
                      dense
                      round
                      icon="visibility"
                      color="primary"
                      @click="openDocument(props.row)"
                      title="Ver documento"
                    />
                    <q-btn
                      size="sm"
                      flat
                      dense
                      round
                      icon="download"
                      color="positive"
                      @click="downloadDocument(props.row)"
                      title="Descargar documento"
                    />
                  </div>
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </div>

        <div v-else class="text-center q-py-lg">
          <q-icon name="folder_open" size="xl" color="grey-5" />
          <p class="text-grey-7 q-mt-md">Selecciona una carpeta para ver sus documentos</p>
        </div>
      </q-card-section>

      <!-- Footer Actions -->
      <q-card-actions align="right" class="bg-grey-1 q-pa-lg">
        <q-btn 
          v-if="isAdmin"
          label="Subir archivos" 
          color="primary" 
          icon="cloud_upload"
          unelevated
          padding="md lg"
          @click="onUpload" 
          :disable="!selectedFolder || uploading || !uploader?.files?.length"
          :loading="uploading"
        />
        <q-btn 
          label="Cerrar" 
          flat 
          padding="md lg"
          v-close-popup 
          @click="close" 
        />
      </q-card-actions>
    </q-card>

    <!-- Dialog para previsualizar -->
    <q-dialog v-model="previewDialog" full-width maximized>
      <q-card>
        <q-card-section class="row items-center bg-grey-9 text-white q-pa-md">
          <div class="text-h6">{{ previewFile?.nombre_original }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pa-none" style="height: calc(100vh - 80px);">
          <iframe
            v-if="previewFile?.archivo"
            :src="previewFile.archivo"
            style="width: 100%; height: 100%; border: none;"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { ability } from 'src/services/ability'
import { Notify } from 'quasar'

const auth = useAuthStore()
const props = defineProps({
  modelValue: Boolean,
  ingresoUuid: {
    type: String,
    required: false,
    default: null
  }
})

// ingreso interno usado para abrir programáticamente
const internalIngresoUuid = ref(props.ingresoUuid)

watch(() => props.ingresoUuid, (v) => {
  internalIngresoUuid.value = v
})

const emit = defineEmits(['update:modelValue', 'uploaded'])

// Determinar si el usuario es admin (usar store central)
const isAdmin = computed(() => {
  return !!auth.isAdmin || auth.rol === 'AD' || (ability && ability.can && ability.can('manage', 'all'))
})

const show = ref(props.modelValue)
const newFolderName = ref('')
const folders = ref([])
const selectedFolder = ref(null)
const uploading = ref(false)
const uploader = ref(null)
const documents = ref([])
const previewDialog = ref(false)
const previewFile = ref(null)
const tablePagination = ref({ rowsPerPage: 10 })

const docColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre_original', align: 'left' },
  { name: 'fecha', label: 'Fecha', field: 'created', align: 'center' },
  { name: 'archivo', label: 'Acciones', field: 'archivo', align: 'right' }
]

watch(() => props.modelValue, (v) => {
  show.value = v
})

watch(show, (v) => {
  emit('update:modelValue', v)
})

const loadFolders = async (ingresoUuid = null) => {
  try {
    const uuidToUse = ingresoUuid || internalIngresoUuid.value
    if (!uuidToUse) {
      folders.value = []
      selectedFolder.value = null
      documents.value = []
      return
    }

    const res = await api.get(`core/documents/folders/?ingreso_uuid=${uuidToUse}`)
    const items = Array.isArray(res.data) ? res.data : (res.data.results || [])
    folders.value = items
    if (items.length) {
      selectedFolder.value = items[0].uuid
      await loadDocuments(items[0].uuid)
    } else {
      selectedFolder.value = null
      documents.value = []
    }
  } catch (err) {
    console.error('Error cargando carpetas:', err)
    Notify.create({ type: 'negative', message: 'Error al cargar carpetas' })
  }
}

onMounted(() => {
  if (internalIngresoUuid.value) {
    loadFolders()
  }
})

watch(() => internalIngresoUuid.value, (v) => {
  if (v) {
    loadFolders(v)
  }
})

// Exponer método para abrir el modal programáticamente desde el padre
function open(ingresoUuid) {
  internalIngresoUuid.value = ingresoUuid
  // abrir diálogo
  show.value = true
  // cargar carpetas para este ingreso
  loadFolders(ingresoUuid)
}

defineExpose({ open })

const foldersOptions = computed(() => folders.value)

async function onFolderSelected(uuid) {
  if (uuid) {
    await loadDocuments(uuid)
  }
}

async function onCreateFolder() {
  if (!newFolderName.value.trim()) {
    Notify.create({ type: 'warning', message: 'Ingresa un nombre para la carpeta' })
    return
  }
  try {
    const payload = { ingreso: props.ingresoUuid, nombre: newFolderName.value }
    await api.post('core/documents/folders/', payload)
    newFolderName.value = ''
    await loadFolders()
    Notify.create({ type: 'positive', message: 'Carpeta creada correctamente' })
  } catch (err) {
    console.error('Error creando carpeta:', err)
    Notify.create({ type: 'negative', message: 'No se pudo crear la carpeta' })
  }
}

function close() {
  show.value = false
}

async function onUpload() {
  if (!selectedFolder.value) {
    Notify.create({ type: 'warning', message: 'Selecciona una carpeta' })
    return
  }
  const files = uploader.value?.files ?? []
  if (!files.length) {
    Notify.create({ type: 'warning', message: 'Selecciona al menos un archivo' })
    return
  }

  uploading.value = true
  try {
    for (const f of files) {
      const form = new FormData()
      form.append('carpeta', selectedFolder.value)
      form.append('archivo', f)
      form.append('nombre_original', f.name)
      await api.post('core/documents/upload/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    }
    Notify.create({ type: 'positive', message: 'Archivos subidos correctamente' })
    emit('uploaded')
    uploader.value.reset()
    await loadDocuments(selectedFolder.value)
  } catch (err) {
    console.error('Error al subir archivos:', err)
    Notify.create({ type: 'negative', message: 'Error al subir los archivos' })
  } finally {
    uploading.value = false
  }
}

function uploaderFactory() {
  return {
    abort(file) {
      console.log('abort', file)
    }
  }
}

async function loadDocuments(folderUuid = null) {
  const uuid = folderUuid || selectedFolder.value
  if (!uuid) {
    documents.value = []
    return
  }
  try {
    const res = await api.get(`core/documents/?carpeta_uuid=${uuid}`)
    const items = Array.isArray(res.data) ? res.data : (res.data.results || [])
    documents.value = items
  } catch (err) {
    console.error('Error cargando documentos:', err.response?.data || err)
    Notify.create({ type: 'negative', message: 'Error al cargar los documentos' })
  }
}

function openDocument(documento) {
  previewFile.value = documento
  previewDialog.value = true
}

async function downloadDocument(documento) {
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
    
    Notify.create({ type: 'positive', message: 'Descarga completada' })
  } catch (err) {
    console.error('Error al descargar:', err)
    Notify.create({ type: 'negative', message: 'Error al descargar el documento' })
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('es-CO', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
:deep(.q-dialog__inner) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.uploader-container {
  transition: all 0.3s ease;
}

.uploader-container:hover {
  background-color: #e3f2fd !important;
  border-color: #1565c0 !important;
}

.hover-row:hover {
  background-color: #f5f5f5;
}
</style>
