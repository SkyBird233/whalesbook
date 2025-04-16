<script setup lang="ts">
import { RouterView } from "vue-router";
import { useBookStore } from "./stores/books";
import { getBooks } from "@/client";
import HeaderComponent from "./components/HeaderComponent.vue";
import { updateAsyncState } from "./utils/state";
import { toRef } from "vue";

const bookStore = useBookStore();

if (!bookStore.books.data) {
  console.log("Fetching books...");
  updateAsyncState(
    toRef(bookStore, "books"),
    getBooks().then((r) => r.data),
  );
}
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
