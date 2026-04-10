<template>
  <q-page class="page-pdf-viewer q-pa-none">
    <div class="pdf-root">
      <div v-if="loading" class="loader-overlay">
        Cargando documento...
      </div>

      <iframe
        v-if="available"
        :src="pdfUrl + pdfQuery"
        class="pdf-frame"
        frameborder="0"
        loading="lazy"
      ></iframe>

      <div v-else class="error-overlay">
        <p>El documento no está disponible en el servidor.</p>
        <p>Por favor agrega el archivo <code>Brochure_previniendo.pdf</code> en <code>/frontend/public/</code> o en la carpeta pública del servidor y recarga la página.</p>
        <q-btn color="primary" :disable="!pdfExistsRemote" @click="openInNewTab" label="Abrir PDF en nueva pestaña" />
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.page-pdf-viewer {
  position: relative;
  min-height: calc(100vh - 64px);
  height: calc(100vh - 64px);
  width: 100%;
  overflow: hidden;
}
.pdf-root {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  background-color: #111;
}
.pdf-frame {
  flex: 1 1 auto;
  width: 100%;
  height: 100%;
  border: none;
  min-height: 0;
}
.loader-overlay,
.error-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  z-index: 1;
}
.error-overlay p {
  margin: 8px 0;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'

const pdfFileName = 'Brochure_previniendo.pdf'
const pdfUrls = [`/${pdfFileName}`, `/public/${pdfFileName}`]
const pdfUrl = ref('')
const pdfExistsRemote = ref(false)
const loading = ref(true)
const available = ref(false)
const pdfQuery = '#toolbar=0&navpanes=0&scrollbar=0'

async function checkPdf() {
  for (const url of pdfUrls) {
    try {
      const resp = await fetch(url, { method: 'HEAD' })
      const ct = resp.headers.get('content-type') || ''
      if (resp && resp.ok && ct.toLowerCase().includes('pdf')) {
        pdfUrl.value = url
        pdfExistsRemote.value = true
        return true
      }
      const r2 = await fetch(url, { method: 'GET' })
      const ct2 = r2.headers.get('content-type') || ''
      if (r2 && r2.ok && ct2.toLowerCase().includes('pdf')) {
        pdfUrl.value = url
        pdfExistsRemote.value = true
        return true
      }
    } catch (err) {
      // ignore and try next URL
    }
  }
  return false
}

function openInNewTab() {
  if (pdfUrl.value) {
    window.open(pdfUrl.value, '_blank')
  }
}

onMounted(async () => {
  const exists = await checkPdf()
  available.value = exists
  loading.value = false
})
</script>
