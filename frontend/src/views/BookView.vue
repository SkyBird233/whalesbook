<script setup lang="ts">
import { useBookStore } from "@/stores/books";
import { watch, computed, onBeforeMount, registerRuntimeCompiler } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getBookState } from "@/client";
import OutLink from "@/components/OutLink.vue";

const route = useRoute();
const router = useRouter();
const bookStore = useBookStore();

const currentBook = computed(() =>
  bookStore.getBook(route.params.name as string)
);

async function refreshState() {
  if (
    currentBook.value &&
    currentBook.value.name &&
    !bookStore.states[currentBook.value.name]
  ) {
    const { data, error } = await getBookState({
      path: { book_name: currentBook.value.name },
    });
    if (!error) {
      bookStore.states[currentBook.value.name] = data;
      return data;
    } else {
      console.error(error);
    }
    // TODO: Error handling
  }
}

onBeforeMount(refreshState); // From home
watch(() => bookStore.books, refreshState); // Direct visit from url

watch(
  () => route.params.name as string,
  async (newName, oldName) => {
    if (!bookStore.books.map((book) => book.name).includes(newName)) {
      router.push("/");
      return;
    }
  }
);
</script>

<template>
  <RouterLink to="/" class="hover:underline"><- back</RouterLink>
  <h2 class="text-2xl pt-2 pd-1">Book {{ currentBook?.name }}</h2>
  <div v-if="currentBook" class="flex flex-col gap-1">
    <div v-for="repo in currentBook.repos">
      <b>{{ repo.name }}</b> | [<OutLink v-if="repo.url" :url="repo.url" />]
      <div v-for="ref in repo.refs" v-if="repo.name" class="border-l pl-[2ch]">
        <div>{{ ref.name?.replace("refs/heads/", "") }}</div>
        <div
          v-if="
            ref.name &&
            currentBook.name &&
            bookStore.states[currentBook.name] &&
            bookStore.states[currentBook.name][repo.name][ref.name].state !==
              'unknown'
          "
          class="pl-[2ch] border-l"
        >
          <div>
            State:
            <i>{{
              bookStore.states[currentBook.name][repo.name][ref.name].state
            }}</i>
          </div>
          <div>
            Preview URL:
            <OutLink
              :url="
                bookStore.states[currentBook.name][repo.name][ref.name].url ??
                ''
              "
              >{{
                bookStore.states[currentBook.name][repo.name][ref.name].url
              }}</OutLink
            >
          </div>
          <div class="wrap-anywhere">
            Git hash:
            {{
              bookStore.states[currentBook.name][repo.name][
                ref.name
              ].build_context?.split("#")[1]
            }}
          </div>
        </div>
        <div v-else class="pl-[2ch] border-l">State: <i>unknown</i></div>
      </div>
    </div>
  </div>
</template>
