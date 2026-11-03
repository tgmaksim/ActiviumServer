<template>
    <RatingSheet
        v-model="isOpen"
        :aria-label="strings.openRating"
    >
        <RatingAverageStats
            :old-avg-mark="ratingData?.oldAvgMark ?? null"
            :new-avg-mark="ratingData?.newAvgMark ?? null"
            :loading="isLoading"
        />

        <div class="rating-my-mark-row">
            <RatingMarkGroup
                v-if="lesson.logs.length"
                :title="lesson.logs.length === 1
                    ? strings.myMark
                    : strings.myMarks"
                :marks="lesson.logs"
            />

            <RatingPraiseButton
                v-if="showPraise"
                :state="lesson.praiseState ?? LoadState.empty()"
                @click="onPraiseClick"
            />
        </div>

        <RatingMarkGroup
            v-if="
                lesson.othersMarks.length &&
                lesson.avgGroupLessonMark
            "
            :title="strings.avgGroupLessonMark"
            :marks="[lesson.avgGroupLessonMark]"
        />

        <p class="rating-info">
            {{ infoText }}
        </p>

        <RatingPeopleList
            :people="lesson.othersMarks"
            :show-number="showNumber"
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

import {
    setShownCacheError,
} from "@/ui-core/state-utils";

import { LoadState } from "@/ui-core/load-state";

import {
    LessonRatingViewModel,
} from "@/views/rating/rating-view-model";

import RatingSheet from "@/components/rating/RatingSheet.vue";
import RatingAverageStats from "@/components/rating/RatingAverageStats.vue";
import RatingMarkGroup from "@/components/rating/RatingMarkGroup.vue";
import RatingPeopleList from "@/components/rating/RatingPeopleList.vue";
import RatingPraiseButton from "@/components/rating/RatingPraiseButton.vue";

import type { UiScheduleLesson } from "../types";
import type { ConfettiOptions } from "@/utils/confetti/confetti-engine";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        lesson: UiScheduleLesson;
        showNumber?: boolean;
    }>(),
    {
        showNumber: false,
    },
);

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
    praise: [
        lessonKey: string,
        confettiOptions: ConfettiOptions,
    ];
}>();

const ratingViewModel = new LessonRatingViewModel();

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

const showPraise = computed(() =>
    !props.lesson.isExtra &&
    props.lesson.lessonKey !== null &&
    props.lesson.praiseState !== null &&
    props.lesson.logs.length > 0 &&
    props.lesson.praiseState.type !== "success",
);

const firstMarkDate = computed(() => {
    const dates = props.lesson.logs
        .map(mark => {
            if (!mark.created) {
                return null;
            }

            const date = new Date(mark.created);

            return Number.isNaN(date.getTime())
                ? null
                : date;
        })
        .filter((date): date is Date => date !== null);

    dates.sort(
        (a, b) => a.getTime() - b.getTime(),
    );

    return dates[0] ?? null;
});

function formatDateTime(date: Date): string {
    const formattedDate = new Intl.DateTimeFormat(
        "ru-RU",
        {
            day: "numeric",
            month: "long",
        },
    ).format(date);

    const formattedTime = new Intl.DateTimeFormat(
        "ru-RU",
        {
            hour: "2-digit",
            minute: "2-digit",
            hourCycle: "h23",
        },
    ).format(date);

    return `${formattedDate} в ${formattedTime}`;
}

const infoText = computed(() => {
    const period = props.lesson.works
        .map(work => work.title)
        .join(", ");

    const additional = firstMarkDate.value
        ? strings.ratingInfoTime(
            formatDateTime(firstMarkDate.value),
        )
        : "";

    return strings.ratingInfo(
        props.lesson.subject,
        period,
        additional,
    );
});

watch(
    () => [
        props.modelValue,
        props.lesson.ratingKey,
    ] as const,
    ([opened, ratingKey]) => {
        if (!opened || !ratingKey) {
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
                if (
                    props.modelValue &&
                    props.lesson.ratingKey
                ) {
                    ratingViewModel.loadCloud(
                        props.lesson.ratingKey,
                    );
                }

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

function onPraiseClick(event: MouseEvent): void {
    const lessonKey = props.lesson.lessonKey;

    if (
        !lessonKey ||
        props.lesson.praiseState?.type === "loading"
    ) {
        return;
    }

    const target = event.currentTarget;

    if (!(target instanceof HTMLElement)) {
        return;
    }

    const rect = target.getBoundingClientRect();

    emit("praise", lessonKey, {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
    });
}
</script>

<style scoped>
.rating-my-mark-row {
    display: flex;
    align-items: center;
    gap: 10px;

    min-width: 0;
}

.rating-info {
    margin: 10px 5px 0;

    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.4;
}
</style>