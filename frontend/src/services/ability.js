import { defineAbility } from '@casl/ability'

// Inicializar ability SIN reglas por defecto. Las reglas se actualizarán
// durante el login mediante `ability.update(rules)` en LoginPage.vue.
const ability = defineAbility(() => {})

export default ability
export { ability }