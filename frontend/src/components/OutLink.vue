<script setup lang="ts">
defineProps<{
  url: string;
}>();
</script>

<template>
  <a
    :href="url"
    target="_blank"
    onclick="event.stopPropagation();"
    class="wrap-anywhere underline hover:underline-offset-3"
    ><slot>{{ url }}</slot></a
  >
</template>
