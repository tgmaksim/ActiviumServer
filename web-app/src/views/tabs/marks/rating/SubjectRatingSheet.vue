<template>
    <RatingSheet
        v-model="isOpen"
        :aria-label="strings.classRating"
    >
        <div
            v-if="isLoading"
            class="rating-loader-container"
        >
            <RatingLoader />
        </div>

        <p
            v-if="infoText"
            class="rating-info"
        >
            {{ infoText }}
        </p>

        <RatingPeopleList
            :people="people"
            show-number
            show-movement
            show-old-mark-info-button
        />
    </RatingSheet>
</template>

<script setup lang="ts">
import {
    computed,
    watch,
} from "vue";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import { setShownCacheError } from "@/ui-core/state-utils";

import {
    SubjectRatingViewModel,
} from "@/views/rating/rating-view-model";

import {
    getSubjectRatingPeople,
} from "@/views/rating/rating-utils";

import RatingSheet from "@/components/rating/RatingSheet.vue";
import RatingLoader from "@/components/rating/RatingLoader.vue";
import RatingPeopleList from "@/components/rating/RatingPeopleList.vue";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        ratingKey: string;
        subject?: string | null;
        classRating?: boolean;
    }>(),
    {
        subject: null,
        classRating: false,
    },
);

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
}>();

const ratingViewModel = new SubjectRatingViewModel();

const isOpen = computed({
    get: () => props.modelValue,
    set: value => emit("update:modelValue", value),
});

const ratingState = computed(
    () => ratingViewModel.state.value,
);

const ratingData = computed(
    () => ratingViewModel.data.value,
);

const isLoading = computed(() =>
    ratingState.value.type === "cacheLoading" ||
    ratingState.value.type === "cloudLoading",
);

const people = computed(() =>
    ratingData.value
        ? getSubjectRatingPeople(ratingData.value)
        : [],
);

const infoText = computed(() => {
    if (props.classRating) {
        return strings.classRatingInfo;
    }

    if (props.subject) {
        return strings.subjectRatingInfo(props.subject);
    }

    return "";
});

watch(
    () => [
        props.modelValue,
        props.ratingKey,
    ] as const,
    ([opened, ratingKey]) => {
        if (!opened) {
            ratingViewModel.reset();
            return;
        }

        ratingViewModel.reset();

        void ratingViewModel.loadCache(ratingKey);
    },
    {
        immediate: true,
    },
);

watch(
    ratingState,
    state => {
        switch (state.type) {
            case "cacheSuccess":
            case "cacheError":
                ratingViewModel.loadCloud(props.ratingKey);

                if (state.type === "cacheError") {
                    Utilities.showUiMessage(state.message);
                }

                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);

                setShownCacheError(ratingViewModel.state);

                break;
        }
    },
);
</script>

<style scoped>
.rating-loader-container {
    display: flex;
    justify-content: center;

    padding: 10px 0;
}

.rating-info {
    margin: 10px 5px 0;

    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.4;
}
</style>