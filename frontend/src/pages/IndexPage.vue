<template>
  <q-page class="q-pa-md q-gutter-sm page-pdf-viewer">
    <div class="pdf-container">
      <div v-if="loading" class="text-center q-pa-md">
        Cargando documento...
      </div>

      <div v-else>
        <iframe
          v-if="available"
          :src="pdfUrl"
          class="pdf-frame"
          frameborder="0"
        ></iframe>

        <div v-else class="q-pa-md text-center">
          <p>El documento no está disponible en el servidor.</p>
          <p>Por favor agrega el archivo <code>Brochure_previniendo.pdf</code> en <code>/frontend/public/</code> o en la carpeta pública del servidor y recarga la página.</p>
          <q-btn color="primary" :disable="!pdfExistsRemote" @click="openInNewTab" label="Abrir PDF en nueva pestaña" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.page-pdf-viewer {
  /* Usar min-height para que el contenedor ocupe al menos la ventana
     sin depender de alturas padre que podrían no estar definidas. */
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}
.pdf-container {
  display: flex;
  flex-direction: column;
  /* Permitir que el contenedor crezca y que el iframe ocupe todo el espacio */
  flex: 1 1 auto;
  min-height: calc(100vh - 64px);
}
.pdf-frame {
  flex: 1 1 auto;
  width: 100%;
  height: 100%;
  min-height: 60vh;
  border: none;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'

const pdfFileName = 'Brochure_previniendo.pdf'
// Intentamos primero en la raíz (desarrollo Quasar), si no existe probamos /public/ (producción nginx)
const pdfUrls = [`/${pdfFileName}`, `/public/${pdfFileName}`]
const pdfUrl = ref('')

const loading = ref(true)
const available = ref(false)
const pdfExistsRemote = ref(false)

async function checkPdf() {
  try {
    for (const url of pdfUrls) {
      try {
        const resp = await fetch(url, { method: 'HEAD' })
        // Verificar que no se trata del index.html (algunos servidores dev devuelven 200 para todo)
        const ct = resp.headers.get('content-type') || ''
        if (resp && resp.ok && ct.toLowerCase().includes('pdf')) {
          pdfUrl.value = url
          available.value = true
          pdfExistsRemote.value = true
          break
        }
        // Si HEAD no devuelve PDF o no es permitido, intentar GET pequeño y validar content-type
        const r2 = await fetch(url, { method: 'GET' })
        const ct2 = r2.headers.get('content-type') || ''
        if (r2 && r2.ok && ct2.toLowerCase().includes('pdf')) {
          pdfUrl.value = url
          available.value = true
          pdfExistsRemote.value = true
          break
        }
      } catch (innerErr) {
        // Ignorar y probar siguiente URL
      }
    }
    if (!available.value) {
      pdfUrl.value = ''
    }
  } catch (err) {
    available.value = false
    pdfUrl.value = ''
  } finally {
    loading.value = false
  }
}

function openInNewTab() {
  window.open(pdfUrl, '_blank')
}

onMounted(() => {
  checkPdf()
})
</script>
