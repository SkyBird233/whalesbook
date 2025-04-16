import { ref } from "vue";
import { defineStore } from "pinia";
import type { Ref } from "vue";
import type { Book } from "@/client";
import type { GetBookStateResponse } from "@/client";
import type { AsyncState } from "@/utils/state";

export const useBookStore = defineStore("books", () => {
  const books: Ref<AsyncState<Book[]>> = ref({ state: "initial", data: null });
  const states: Ref<{ [bookName: string]: AsyncState<GetBookStateResponse> }> =
    ref({});

  function getBook(bookName: string) {
    if (books.value.state == "ready")
      return books.value.data.filter((p) => p.name == bookName)[0];
  }

  return { books, states, getBook };
});
