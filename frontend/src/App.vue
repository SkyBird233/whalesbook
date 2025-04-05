<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterView } from "vue-router";
import { useBookStore } from "./stores/books";
import { getBooks } from "@/client";

const bookStore = useBookStore();

onBeforeMount(async () => {
  if (bookStore.books.length === 0) {
    console.log("Fetching books...");
    const { data, error } = await getBooks();
    bookStore.books = data ?? [];
  }
});
</script>

<template>
  <div class="flex items-center justify-center h-screen">
    <main class="max-w-xl">
      <RouterView />
    </main>
  </div>
</template>

<style scoped></style>
