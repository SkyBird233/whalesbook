import { ref } from "vue";
import { defineStore } from "pinia";

export const useBookStore = defineStore("books", () => {
  const books = ref([]);

  return { books };
});
