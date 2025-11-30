<template>
  <div id="q-app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style lang="scss">
  .my-swal {
    z-index: 10000000000!important;
  }
  .width-short {
    width: 200px!important;
    white-space: normal!important;
    font-size: 0.85em;
    font-style: italic;
    color: #555;
    margin-top: 4px;
  }
  thead tr:first-child th {
    position: sticky!important;
    top: 0!important;
    opacity: 1!important;
    text-transform: uppercase!important;
  }
</style>