import type { Ref } from "vue";

export type AsyncState<T> =
  | { state: "initial"; data: null }
  | { state: "loading"; data: null }
  | { state: "ready"; data: T }
  | { state: "error"; data: null; error: string | object | unknown };

export function updateAsyncState<T>(
  asyncState: Ref<AsyncState<T>>,
  promise: Promise<T>,
) {
  asyncState.value = { state: "loading", data: null };
  (async () => {
    try {
      const data = await promise;
      asyncState.value = { state: "ready", data: data };
    } catch (error) {
      asyncState.value = { state: "error", data: null, error };
      console.error(error);
    }
  })();
}
