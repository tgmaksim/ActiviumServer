<template>
    <div class="rating-list">
        <div
            v-for="(person, index) in people"
            :key="person.personKey ?? `${person.name}-${index}`"
            class="rating-person"
            :class="{
                'rating-person-old': person.isOldMark,
            }"
        >
            <span
                v-if="showNumber"
                class="rating-person-number"
            >
                {{
                    person.number !== null
                        ? strings.personNumber(person.number + 1)
                        : ""
                }}
            </span>

            <img
                v-if="showMovement && person.isRatingUp === true"
                class="rating-person-arrow"
                :src="arrowUp"
                alt=""
            />

            <img
                v-else-if="showMovement && person.isRatingUp === false"
                class="rating-person-arrow"
                :src="arrowDown"
                alt=""
            />

            <div class="rating-person-name">
                <span>{{ person.name }}</span>

                <button
                    v-if="showOldMarkInfoButton && person.isOldMark"
                    class="rating-info-button"
                    type="button"
                    :aria-label="strings.oldMarkInfo"
                    @click="showOldMarkInfo"
                >
                    <img
                        :src="infoIcon"
                        alt=""
                    />
                </button>
            </div>

            <div class="rating-person-marks">
                <MarkBadge
                    v-for="(mark, markIndex) in person.marks"
                    :key="markIndex"
                    :mark="mark"
                    size="rating"
                />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import MarkBadge from "@/components/MarkBadge.vue";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import arrowUp from "@/assets/rating/arrow_up.svg";
import arrowDown from "@/assets/rating/arrow_down.svg";
import infoIcon from "@/assets/rating/info.svg";

import type { RatingPerson } from "@/views/rating/rating-utils";

withDefaults(
    defineProps<{
        people: readonly RatingPerson[];
        showNumber?: boolean;
        showMovement?: boolean;
        showOldMarkInfoButton?: boolean;
    }>(),
    {
        showNumber: false,
        showMovement: false,
        showOldMarkInfoButton: false,
    },
);

function showOldMarkInfo(): void {
    Utilities.showText(strings.oldMarkInfo, true);
}
</script>

<style scoped>
.rating-list {
    display: flex;
    flex-direction: column;
    gap: 3px;

    margin-top: 12px;
    padding-bottom: 12px;
}

.rating-person {
    display: flex;
    align-items: center;
    gap: 5px;

    min-width: 0;
    padding: 4px 5px;
}

.rating-person-old {
    border-radius: 8px;
    background: var(--bg-old-rating-mark);
}

.rating-person-number {
    flex: 0 0 auto;

    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
}

.rating-person-arrow {
    flex: 0 0 auto;

    width: 18px;
    height: 22px;

    object-fit: contain;
}

.rating-person-name {
    display: flex;
    flex: 1 1 auto;
    align-items: center;
    gap: 4px;

    min-width: 0;
    margin-left: 5px;

    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
}

.rating-person-name > span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rating-info-button {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    width: 22px;
    height: 26px;
    padding: 2px;

    border: 0;
    background: transparent;

    cursor: pointer;
}

.rating-info-button img {
    width: 16px;
    height: 16px;

    object-fit: contain;
}

.rating-person-marks {
    display: flex;
    flex: 0 0 auto;
    gap: 4px;

    max-width: 55%;
    overflow-x: auto;

    scrollbar-width: none;
}

.rating-person-marks::-webkit-scrollbar {
    display: none;
}
</style>