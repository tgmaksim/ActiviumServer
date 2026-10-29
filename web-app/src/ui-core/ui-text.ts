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

export const UiText = {
    stringResource(
        key: StringResourceKey,
        args: readonly unknown[] = [],
    ): UiText {
        return {
            type: "stringResource",
            key,
            args,
        };
    },

    dynamicString(value: string): UiText {
        return {
            type: "dynamicString",
            value,
        };
    },
};