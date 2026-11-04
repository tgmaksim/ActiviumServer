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
                :title="strings.myMark"
                :marks="[mark]"
            />

            <RatingPraiseButton
                v-if="ratingData?.hasAbilityPraise"
                :state="praiseState"
                @click="openPraiseDialog"
            />
        </div>

        <RatingMarkGroup
            v-if="ratingData?.avgGroupMark"
            :title="strings.avgGroupWorkMark"
            :marks="[ratingData.avgGroupMark]"
        />

        <p class="rating-info">
            {{ infoText }}
        </p>

        <RatingPeopleList
            :people="ratingData?.othersMarks ?? []"
        />
    </RatingSheet>

    <PraiseDialog
        :visible="showPraiseDialog"
        @close="showPraiseDialog = false"
        @submit="submitPraise"
    />
</template>

<script setup lang="ts">
import {
    computed,
    ref,
    watch,
} from "vue";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import { MarkRatingViewModel } from "@/views/rating/rating-view-model";

import { LoadState } from "@/ui-core/load-state";
import { setShownCacheError } from "@/ui-core/state-utils";

import { useConfetti } from "@/composables/useConfetti";
import type { ConfettiOptions } from "@/utils/confetti/confetti-engine";

import RatingSheet from "./RatingSheet.vue";
import RatingAverageStats from "./RatingAverageStats.vue";
import RatingMarkGroup from "./RatingMarkGroup.vue";
import RatingPeopleList from "./RatingPeopleList.vue";
import RatingPraiseButton from "./RatingPraiseButton.vue";

import PraiseDialog from "@/components/PraiseDialog.vue";

import type { MarkLog } from "@/api/dnevnik";

const props = defineProps<{
    modelValue: boolean;
    ratingKey: string;
    subject: string;
    mark: MarkLog;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
}>();

const ratingViewModel = new MarkRatingViewModel();

const {
    startConfettiAnimation,
} = useConfetti();

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

const praiseState = computed(
    () => ratingViewModel.praiseState.value,
);

const isLoading = computed(() =>
    ratingState.value.type === "cacheLoading" ||
    ratingState.value.type === "cloudLoading",
);

const showPraiseDialog = ref(false);

const praiseConfettiOptions = ref<ConfettiOptions>({});

/**
 * Форматируем дату выставления оценки
 * в соответствии с Android.
 */
function formatMarkDate(value: string | null): string {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

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
    const additional = formatMarkDate(props.mark.created);

    return strings.ratingInfo(
        props.subject,
        props.mark.work?.title ?? "",
        additional
            ? strings.ratingInfoTime(additional)
            : "",
    );
});

/**
 * Загружаем кэш при открытии или смене оценки.
 */
watch(
    () => [
        props.modelValue,
        props.ratingKey,
    ] as const,
    ([opened, ratingKey]) => {
        if (!opened) {
            ratingViewModel.reset();
            ratingViewModel.resetPraise();
            showPraiseDialog.value = false;
            return;
        }

        ratingViewModel.reset();
        ratingViewModel.resetPraise();

        void ratingViewModel.loadCache(ratingKey);
    },
    {
        immediate: true,
    },
);

/**
 * После чтения кэша обновляем данные с сервера.
 */
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

/**
 * Обработка отправки похвалы.
 */
watch(
    praiseState,
    state => {
        if (state.type === "error") {
            Utilities.showUiMessage(state.message);

            ratingViewModel.resetPraiseError();
            return;
        }

        if (state.type !== "success") {
            return;
        }

        Utilities.showText(strings.praiseSent);

        ratingViewModel.resetPraise();

        showPraiseDialog.value = false;
        emit("update:modelValue", false);

        startConfettiAnimation(
            praiseConfettiOptions.value,
        );
    },
);

function openPraiseDialog(event: MouseEvent): void {
    if (
        praiseState.value.type === "loading" ||
        !ratingData.value?.hasAbilityPraise
    ) {
        return;
    }

    const target = event.currentTarget;

    if (target instanceof HTMLElement) {
        const rect = target.getBoundingClientRect();

        praiseConfettiOptions.value = {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
        };
    }

    showPraiseDialog.value = true;
}

function submitPraise(text: string | null): void {
    if (praiseState.value.type === "loading") {
        return;
    }

    showPraiseDialog.value = false;

    ratingViewModel.sendPraise(
        props.ratingKey,
        text,
    );
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