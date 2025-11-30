import { defineBoot } from '#q-app/wrappers'
import { createI18n } from 'vue-i18n'
import messages from 'src/i18n'

export default defineBoot(({ app }) => {
  const i18n = createI18n({
    // <-- modo Composition API:
    legacy: false,

    // idioma por defecto:
    locale: 'es-ES',

    // idioma de respaldo:
    fallbackLocale: 'en-US',

    // permite la inyección global de `t()` y `$t()`:
    globalInjection: true,

    // tus mensajes:
    messages
  })

  app.use(i18n)
})
