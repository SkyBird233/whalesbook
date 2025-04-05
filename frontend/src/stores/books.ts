import { ref } from "vue";
import { defineStore } from "pinia";
import type { Ref } from "vue";
import type { Book } from "@/client";
import type { GetBookStateResponse } from "@/client";

export const useBookStore = defineStore("books", () => {
  const books: Ref<Book[]> = ref([]);
  const states: Ref<{ [bookName: string]: GetBookStateResponse }> = ref({});

  function getBook(bookName: string) {
    return books.value.filter((v, i, a) => v.name == bookName)[0];
  }

  return { books, states, getBook };
});
