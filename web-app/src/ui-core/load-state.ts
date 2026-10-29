import type { UiText } from "./ui-text";

export type LoadState<T> =
    | {
          type: "empty";
      }
    | {
          type: "loading";
      }
    | {
          type: "error";
          message: UiText;
      }
    | {
          type: "shownError";
      }
    | {
          type: "success";
          data: T;
      };

export const LoadState = {
    empty(): LoadState<never> {
        return { type: "empty" };
    },

    loading(): LoadState<never> {
        return { type: "loading" };
    },

    error(message: UiText): LoadState<never> {
        return {
            type: "error",
            message,
        };
    },

    shownError(): LoadState<never> {
        return { type: "shownError" };
    },

    success<T>(data: T): LoadState<T> {
        return {
            type: "success",
            data,
        };
    },
};