<script setup lang="ts">
import { useBookStore } from "@/stores/counter";
import { RouterLink } from "vue-router";

const bookStore = useBookStore();
if (bookStore.books.length === 0) {
  console.log("Fetching books")
  fetch("/api/v1/books")
    .then((r) => r.json())
    .then((j) => (bookStore.books = j));
}
</script>

<template>
  <main>
    <h2>Books</h2>
    <ul>
      <li v-for="book in bookStore.books">
        <RouterLink :to="`/books/${book.name}`">{{ book.name }}</RouterLink>
      </li>
    </ul>
  </main>
</template>
