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
    class="underline wrap-anywhere hover:underline-offset-3"
    >{{ url }}</a
  >
</template>
