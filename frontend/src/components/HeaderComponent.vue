<script setup lang="ts">
import OutLink from "./OutLink.vue";
</script>

<template>
  <header class="grid grid-cols-3 border-b px-2 py-1">
    <RouterLink to="/" v-if="$route.path !== '/'" class="hover:underline"
      >←back</RouterLink
    >
    <div v-else></div>
    <div class="text-center">whalesbook</div>
    <OutLink url="https://github.com/SkyBird233/whalesbook" class="text-right"
      >GitHub</OutLink
    >
  </header>
</template>
