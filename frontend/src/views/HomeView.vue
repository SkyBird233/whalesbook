<script setup lang="ts">
import { useBookStore } from "@/stores/counter";
import { RouterLink } from "vue-router";

import { getBooks } from "@/client";
import { onMounted } from "vue";

const bookStore = useBookStore();

onMounted(async () => {
  if (bookStore.books.length === 0) {
    console.log("Fetching books...");
    const { data, error } = await getBooks();
    bookStore.books = data ?? [];
  }
});
</script>

<template>
  <main>
    <h2>Books</h2>
    <ul>
      <li v-for="book in bookStore.books" class="p-2">
        <RouterLink :to="`/books/${book.name}`">{{ book.name }}</RouterLink>
      </li>
    </ul>
  </main>
</template>
