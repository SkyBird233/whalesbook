<script setup lang="ts">
import { useBookStore } from "@/stores/books";
import OutLink from "@/components/OutLink.vue";

const bookStore = useBookStore();
</script>

<template>
  <h2 class="text-2xl pb-2">Books</h2>
  <div class="flex flex-col gap-4">
    <div
      @click="$router.push(`/books/${book.name}`)"
      v-for="book in bookStore.books"
      class="outline p-2 cursor-pointer hover:shadow-2xl"
    >
      <h3 class="text-xl">{{ book.name }}</h3>
      <div class="grid grid-cols-[min-content_1fr] gap-x-2">
        <template v-for="repo in book.repos">
          <div>{{ repo.name }}</div>
          <OutLink v-if="repo.url" :url="repo.url"
        /></template>
      </div>
    </div>
  </div>
</template>
