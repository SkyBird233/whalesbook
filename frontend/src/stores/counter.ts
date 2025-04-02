import { ref } from "vue";
import { defineStore } from "pinia";
import type { Ref } from "vue";
import type { Book } from "@/client";

export const useBookStore = defineStore("books", () => {
  const books: Ref<Book[]> = ref([]);

  return { books };
});
