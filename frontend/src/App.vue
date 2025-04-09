<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterView } from "vue-router";
import { useBookStore } from "./stores/books";
import { getBooks } from "@/client";

const bookStore = useBookStore();

onBeforeMount(async () => {
  if (bookStore.books.length === 0) {
    console.log("Fetching books...");
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { data, error } = await getBooks();
    bookStore.books = data ?? [];
  }
});
</script>

<template>
  <div class="flex items-center-safe justify-center-safe h-screen overflow-auto">
    <main class="flex-1 min-w-3xs max-w-[min(var(--container-lg),100vw)] p-2">
      <RouterView />
    </main>
  </div>
</template>

<style scoped></style>
