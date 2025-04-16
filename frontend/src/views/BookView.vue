<script setup lang="ts">
import { useBookStore } from "@/stores/books";
import { watch, computed, toRef } from "vue";
import { useRoute } from "vue-router";
import { getBookState } from "@/client";
import OutLink from "@/components/OutLink.vue";
import { updateAsyncState } from "@/utils/state";

const route = useRoute();
const bookStore = useBookStore();

const currentBook = computed(() =>
  bookStore.getBook(route.params.name as string),
);

const currentBookState = computed(() =>
  currentBook.value?.name ? bookStore.states?.[currentBook.value.name] : null,
);

function lazyUpdateCurrentBookState() {
  if (currentBook.value?.name) {
    if (!currentBookState.value) console.log("Fetching book state...");
    updateAsyncState(
      toRef(bookStore.states, currentBook.value.name),
      getBookState({ path: { book_name: currentBook.value.name } }).then(
        (r) => r.data,
      ),
    );
  }
}

lazyUpdateCurrentBookState();
watch(() => bookStore.books, lazyUpdateCurrentBookState);
</script>

<template>
  <h2 class="pd-2 text-2xl">Book {{ currentBook?.name }}</h2>
  <div v-if="currentBook" class="flex flex-col gap-1">
    <div v-for="repo in currentBook.repos" :key="repo.name">
      <b>{{ repo.name }}</b> | [<OutLink v-if="repo.url" :url="repo.url" />]
      <div v-for="ref in repo.refs" :key="ref.name" class="border-l pl-[2ch]">
        <div>{{ ref.name.replace("refs/heads/", "") }}</div>
        <div
          v-if="currentBookState?.state === 'ready'"
          class="border-l pl-[2ch]"
        >
          <template
            v-if="
              currentBookState.data[repo.name][ref.name].state !== 'unknown'
            "
          >
            <div>
              State:
              <i>{{ currentBookState.data[repo.name][ref.name].state }}</i>
            </div>
            <div>
              Preview URL:
              <OutLink
                :url="currentBookState.data[repo.name][ref.name].url ?? ''"
                >{{ currentBookState.data[repo.name][ref.name].url }}</OutLink
              >
            </div>
            <div class="wrap-anywhere">
              Git hash:
              {{
                currentBookState.data[repo.name][ref.name].build_context?.split(
                  "#",
                )[1]
              }}
            </div>
          </template>
          <div v-else>State: <i>unknown</i></div>
        </div>
        <div
          v-else-if="currentBookState?.state === 'loading'"
          class="border-l pl-[2ch]"
        >
          State: <i>loading...</i>
        </div>
        <div
          v-else-if="currentBookState?.state === 'error'"
          class="border-l pl-[2ch]"
        >
          Error: {{ currentBookState.error }}
        </div>
      </div>
    </div>
  </div>
  <div v-else>Failed to get current book</div>
</template>
