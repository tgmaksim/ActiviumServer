<template>
    <BottomSheet
        v-model="isOpen"
        :aria-label="ariaLabel"
    >
        <div class="rating-sheet">
            <slot />
        </div>
    </BottomSheet>
</template>

<script setup lang="ts">
import { computed } from "vue";

import BottomSheet from "@/components/BottomSheet.vue";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        ariaLabel?: string;
    }>(),
    {
        ariaLabel: undefined,
    },
);

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
}>();

const isOpen = computed({
    get: () => props.modelValue,
    set: value => emit("update:modelValue", value),
});
</script>

<style scoped>
.rating-sheet {
    box-sizing: border-box;
    width: 100%;

    padding: 0 10px 16px;
}
</style>