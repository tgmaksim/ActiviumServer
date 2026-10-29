import type { UiText } from "./ui-text";

export type CacheDataLoadState =
    | {
          type: "empty";
      }
    | {
          type: "cacheLoading";
      }
    | {
          type: "cacheSuccess";
      }
    | {
          type: "cacheError";
          message: UiText;
      }
    | {
          type: "cloudLoading";
      }
    | {
          type: "cloudSuccess";
      }
    | {
          type: "cloudError";
          message: UiText;
      }
    | {
          type: "shownError";
      };

export const CacheDataLoadState = {
    empty(): CacheDataLoadState {
        return { type: "empty" };
    },

    cacheLoading(): CacheDataLoadState {
        return { type: "cacheLoading" };
    },

    cacheSuccess(): CacheDataLoadState {
        return { type: "cacheSuccess" };
    },

    cacheError(message: UiText): CacheDataLoadState {
        return {
            type: "cacheError",
            message,
        };
    },

    cloudLoading(): CacheDataLoadState {
        return { type: "cloudLoading" };
    },

    cloudSuccess(): CacheDataLoadState {
        return { type: "cloudSuccess" };
    },

    cloudError(message: UiText): CacheDataLoadState {
        return {
            type: "cloudError",
            message,
        };
    },

    shownError(): CacheDataLoadState {
        return { type: "shownError" };
    },
};