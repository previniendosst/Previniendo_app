<template>
    <q-page class="q-pa-md q-gutter-sm">
        <div class="row q-mb-md">
            <div class="col-12">
                <div class="text-h5">Mi Espacio</div>
                <div class="text-subtitle2 text-grey-7">Visualiza los ingresos asignados a tu cuenta</div>
            </div>
        </div>

        <q-inner-loading :showing="visible">
            <q-spinner-pie color="primary" size="70px" />
        </q-inner-loading>

        <div v-if="!visible" class="row q-gutter-lg">
            <div v-for="ingreso in ingresosDelUsuario" :key="ingreso.uuid" class="col-12 col-md-6 col-lg-4">
                <q-card class="full-height">
                    <q-card-section>
                        <div class="row items-start q-gutter-md">
                            <div class="col">
                                <div class="text-h6">{{ ingreso.nombre }}</div>
                                <div class="text-body2 text-grey-7">
                                    {{ ingreso.tipo_ingreso.descripcion }}
                                </div>
                            </div>
                            <div class="col-auto">
                                <q-badge
                                    :color="ingreso.tipo_ingreso.codigo === 'conjunto' ? 'info' : 'primary'"
                                    text-color="white"
                                >
                                    {{ ingreso.tipo_ingreso.codigo.toUpperCase() }}
                                </q-badge>
                            </div>
                        </div>
                    </q-card-section>

                    <q-separator />

                    <q-card-section>
                        <div class="q-gutter-md">
                            <div>
                                <div class="text-overline">NIT</div>
                                <div class="text-body1">{{ ingreso.nit }}</div>
                            </div>
                            <div>
                                <div class="text-overline">Dirección</div>
                                <div class="text-body2">{{ ingreso.direccion }}</div>
                            </div>
                            <div>
                                <div class="text-overline">Administrador</div>
                                <div class="text-body2">{{ ingreso.nombre_admin }}</div>
                            </div>
                            <div>
                                <div class="text-overline">Contacto</div>
                                <div class="text-body2">
                                    <div>📧 {{ ingreso.correo }}</div>
                                    <div>📱 {{ ingreso.telefono }}</div>
                                </div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <div v-if="!visible && ingresosDelUsuario.length === 0" class="row">
            <div class="col-12">
                <q-banner class="bg-info text-white">
                    <template v-slot:avatar>
                        <q-icon name="info" />
                    </template>
                    No tienes ingresos asignados. Contacta con el administrador para que te asigne un ingreso.
                </q-banner>
            </div>
        </div>
    </q-page>
</template>

<style lang="scss"></style>

<script setup>
// Importacion de librerias
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'

// Constantes
const auth = useAuthStore()

// Declaracion de variables
const ingresosDelUsuario = ref([])
const visible = ref(false)

onMounted(() => {
    loadIngresosDelUsuario()
})

// Funciones
async function loadIngresosDelUsuario() {
    visible.value = true
    try {
        const response = await api.get('seguridad/perfil/')
        ingresosDelUsuario.value = response.data.ingresos.map(ui => ui.ingreso)
    } catch (error) {
        console.error('Error al cargar ingresos:', error)
    } finally {
        visible.value = false
    }
}
</script>
