import type { strings } from "@/constants/strings";

export type StringResourceKey = keyof typeof strings;

export type UiText =
    | {
          type: "stringResource";
          key: StringResourceKey;
          args?: readonly unknown[];
      }
    | {
          type: "dynamicString";
          value: string;
      };