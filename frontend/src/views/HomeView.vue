<script setup lang="ts">
import { useBookStore } from "@/stores/books";
import OutLink from "@/components/OutLink.vue";

const bookStore = useBookStore();
</script>

<template>
  <h2 class="pb-2 text-2xl">Books</h2>
  <div class="flex flex-col gap-4" v-if="bookStore.books.state === 'ready'">
    <div
      @click="$router.push(`/books/${book.name}`)"
      v-for="book in bookStore.books.data"
      :key="book.name"
      class="cursor-pointer p-2 outline hover:shadow-2xl"
    >
      <h3 class="text-xl">{{ book.name }}</h3>
      <div class="grid grid-cols-[min-content_1fr] gap-x-2">
        <template v-for="repo in book.repos" :key="repo.name">
          <div>{{ repo.name }}</div>
          <OutLink v-if="repo.url" :url="repo.url" class="max-w-fit" />
          <ul class="col-start-2">
            <li v-for="ref in repo.refs" :key="ref.name">
              - {{ ref.name?.replace("refs/heads/", "") }}
            </li>
          </ul>
        </template>
      </div>
    </div>
  </div>
  <div v-else-if="bookStore.books.state === 'loading'">Loading books...</div>
  <div v-else-if="bookStore.books.state === 'error'">
    Error: {{ bookStore.books.error }}
  </div>
</template>
