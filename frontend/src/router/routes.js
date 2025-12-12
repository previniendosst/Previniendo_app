
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'index', component: () => import('pages/IndexPage.vue'), meta: { requiresAuth: true } },
      { path: 'usuarios', name: 'usuarios', component: () => import('pages/UsuariosPage.vue'), meta: { requiresAuth: true, requiredPermission: { action: 'read', subject: 'Usuarios' } } },
      { path: 'ingresos', name: 'ingresos', component: () => import('pages/IngresosPage.vue'), meta: { requiresAuth: true, requiredPermission: { action: 'read', subject: 'Ingresos' } } },
      { path: 'roles', name: 'roles', component: () => import('pages/RolesPage.vue'), meta: { requiresAuth: true, requiredPermission: { action: 'read', subject: 'Roles' } } },
      { path: 'mi-espacio', name: 'mi-espacio', component: () => import('pages/MiEspacioPage.vue'), meta: { requiresAuth: true, requiredPermission: { action: 'read', subject: 'MiEspacio' } } }
    ]
  },
  { path: '/login', name: 'login', component: () => import('pages/LoginPage.vue') }
]

// Always leave this as last one
if (process.env.MODE !== 'ssr') {
  routes.push({
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  })
}

export default routes

