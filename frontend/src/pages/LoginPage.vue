<template>
  <div class="login-container">
    <!-- Canvas animado de fondo -->
    <canvas id="bg-canvas"></canvas>

    <!-- Tarjeta del login -->
    <q-card class="login-card">
      <q-card-section>
        <div class="text-h5 text-primary text-center q-mb-md">
          Iniciar Sesión
        </div>

        <!-- Logo dentro del modal -->
        <div class="logo-modal-wrapper">
          <img :src="logo" alt="Logo" class="logo-modal" />
        </div>

        <!-- 🔥 SE ARREGLA AQUÍ -->
        <q-input
          v-model="login_form.username"
          label="Usuario"
          filled
          dense
          clearable
          class="q-mb-md"
        >
          <template #prepend>
            <q-icon name="person" color="primary" />
          </template>
        </q-input>

        <q-input
          v-model="login_form.password"
          type="password"
          label="Contraseña"
          filled
          dense
          clearable
          class="q-mb-md"
        >
          <template #prepend>
            <q-icon name="lock" color="primary" />
          </template>
        </q-input>

        <q-btn
          color="primary"
          label="Ingresar"
          class="full-width q-mt-sm"
          unelevated
          @click="login"
          :loading="loading"
          :disable="loading"
        />

        <div class="text-center q-mt-md">
          <a href="#" @click="openModal()">¿Olvidaste tu contraseña?</a>
        </div>

        <q-banner v-if="error_login" class="bg-negative text-white q-mt-md">
          {{ error_login }}
        </q-banner>

      </q-card-section>
    </q-card>

    <!-- Modal recuperar contraseña -->
    <q-dialog v-model="modalOlvidasteContrasena" persistent>
      <q-card style="min-width: 300px">
        <q-card-section>
          <div class="text-h6">Recuperar contraseña</div>
          <p class="text-body2">
            Por favor ingresa tu correo para enviarte una nueva contraseña.
          </p>
        </q-card-section>

        <q-card-section>
          <q-input
            filled
            v-model="email_olvidaste_contrasena"
            label="Correo electrónico"
            type="email"
            clearable
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn color="red" label="Cancelar" v-close-popup />
          <q-btn color="secondary" label="Enviar" @click="submitReset()" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>

import { AbilityBuilder } from '@casl/ability'
import { useAuthStore } from 'src/stores/auth';
import { useRouter } from 'vue-router';
import { ref, onMounted, watch } from 'vue';
import { ability } from 'src/services/ability';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar'

import logo from "src/assets/logo.png";


const auth = useAuthStore()
const router = useRouter()
const $q = useQuasar()

const form_login = ref(null)
const login_form = ref({ "username": '', "password": '' })
const loading = ref(false)
const error_login = ref('')
const modalOlvidasteContrasena = ref(false)
const email_olvidaste_contrasena = ref('')

async function login() {
  if (login_form.value.username === '' || login_form.value.password === '') {
    $q.notify({ 
      type: 'warning', 
      message: 'Por favor ingresa tu usuario y contraseña.',
      position: 'top', 
    })
    return
  }

  try {
    loading.value = true

    await auth.login({ ...login_form.value })

    router.push({ name: 'index' })

  } catch (error) {
    if (error.response && (error.response.status === 400 || error.response.status === 401)) {
      error_login.value = 'Usuario o contraseña incorrectos'
      console.log('Error aqui')
    } else {
      error_login.value = 'Error de conexión'
    }
  }
  finally {
    loading.value = false
  }
}

function openModal() {
  email_olvidaste_contrasena.value = ''
  modalOlvidasteContrasena.value = true
}

async function submitReset() {
  if (!email_olvidaste_contrasena.value) {
    $q.notify({ type: 'warning', message: 'Por favor ingresa tu correo.' })
    return
  }
  loading.value = true
  try {
    const response = await api.post('/seguridad/verificar_correo/', { email: email_olvidaste_contrasena.value })

    if (!response) {
      $q.notify({ type: 'negative', message: 'Error al enviar el enlace.' })
      return
    }

    $q.notify({
      type: 'positive',
      message: `Se envio la nueva contraseña al correo: ${email_olvidaste_contrasena.value}`,
      position: 'top',
      textColor: 'black',
      icon: 'check_circle',
    })

    modalOlvidasteContrasena.value = false
  }
  finally {
    loading.value = false
  }
}

watch(
  () => auth.rol,
  (newRol) => {
    const { can, rules } = new AbilityBuilder(ability.constructor)

    switch (newRol) {
      case 'AD':
        can('manage', 'all')
        can(['create', 'read', 'update', 'delete', 'detail', 'finish'], ['Usuarios'])
        break
      default:
        break
    }

    ability.update(rules)
  }
)

watch([() => login_form.value.username, () => login_form.value.password], () => {
  error_login.value = ''
})

onMounted(() => {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  const colors = ["#64b5f6", "#42a5f5", "#90caf9", "#1e88e5"];

  const dots = Array.from({ length: 65 }).map(() => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: 12 + Math.random() * 8,     // ⭐ más grandes
    dx: (Math.random() - 0.5) * 0.4,
    dy: (Math.random() - 0.5) * 0.4,
    color: colors[Math.floor(Math.random() * colors.length)]
  }));

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    dots.forEach((d) => {
      d.x += d.dx;
      d.y += d.dy;

      if (d.x < 0 || d.x > canvas.width) d.dx *= -1;
      if (d.y < 0 || d.y > canvas.height) d.dy *= -1;

      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      ctx.fillStyle = d.color;
      ctx.fill();
    });

    for (let i = 0; i < dots.length; i++) {
      for (let j = i + 1; j < dots.length; j++) {
        const dx = dots[i].x - dots[j].x;
        const dy = dots[i].y - dots[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 180) {
          ctx.beginPath();
          ctx.strokeStyle = "#64b5f6";
          ctx.lineWidth = 3;  // ⭐ más gruesas
          ctx.moveTo(dots[i].x, dots[i].y);
          ctx.lineTo(dots[j].x, dots[j].y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animate);
  }

  animate();
});
</script>


<style scoped>
.login-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;

  /* 🔵 Fondo crema suave */
  background: #fdf8f2 !important; /* tono crema inspirado en papelería */
}

#bg-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* Logo */
.login-logo {
  width: 180px;
  position: relative;
  z-index: 10;
  display: block;
  margin: 40px auto 20px auto;
}

/* Card */
.login-card {
  width: 350px;
  margin: 0 auto;
  margin-top: 300px;
  padding-top: 10px;

  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(6px);
  border-radius: 16px;

  box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.13);
  z-index: 10;
}
.logo-modal-wrapper {
  text-align: center;
  margin-bottom: 10px;
  margin-top: -10px;
}

.logo-modal {
  width: 120px;
  opacity: 0.95;
  display: block;
  margin: 0 auto 10px auto;
}

.text-primary {
  color: #1e88e5 !important;
}
.full-width {
  width: 100%;
}
</style>
