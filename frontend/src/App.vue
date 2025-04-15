<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterView } from "vue-router";
import { useBookStore } from "./stores/books";
import { getBooks } from "@/client";
import HeaderComponent from "./components/HeaderComponent.vue";

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
  <div class="flex h-screen justify-center-safe overflow-auto">
    <div class="max-w-[min(var(--container-2xl),100vw)] min-w-3xs flex-1">
      <HeaderComponent />
      <main class="m-2">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped></style>
