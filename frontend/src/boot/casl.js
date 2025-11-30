import { boot } from 'quasar/wrappers'
import { Can, abilitiesPlugin } from '@casl/vue'
import { ability } from 'src/services/ability'

export default boot(({ app }) => {
  app.use(abilitiesPlugin, ability)
  app.component(Can.name, Can) 
})
