<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import scheduleIcon from "@/assets/menu/schedule.svg?raw";
import marksIcon from "@/assets/menu/marks.svg?raw";
import schoolIcon from "@/assets/menu/school.svg?raw";
import settingsIcon from "@/assets/menu/settings.svg?raw";

const route = useRoute();

const items = [
    { name: "schedule", label: "Расписание", icon: scheduleIcon },
    { name: "marks", label: "Оценки", icon: marksIcon },
    { name: "school", label: "Актив", icon: schoolIcon },
    { name: "settings", label: "Настройки", icon: settingsIcon },
] as const;

const current = computed(() => {
    const matchedRoute = [...route.matched]
        .reverse()
        .find((record) =>
            items.some((item) => item.name === record.name),
        );

    return matchedRoute?.name ?? "schedule";
});

function getIconSvg(svg: string): string {
    return svg
        .replace(/fill="#[0-9a-fA-F]{3,8}"/g, 'fill="currentColor"')
        .replace(/stroke="#[0-9a-fA-F]{3,8}"/g, 'stroke="currentColor"');
}
</script>

<template>
    <nav class="bottom-navigation" aria-label="Основная навигация">
        <RouterLink
            v-for="item in items"
            :key="item.name"
            :to="{ name: item.name }"
            class="navigation-item"
            :class="{
                'navigation-item--active': current === item.name,
            }"
            :aria-current="current === item.name ? 'page' : undefined"
        >
            <span
                class="navigation-item__icon"
                v-html="getIconSvg(item.icon)"
            />

            <span
                v-if="current === item.name"
                class="navigation-item__label"
            >
                {{ item.label }}
            </span>
        </RouterLink>
    </nav>
</template>

<style scoped>
.bottom-navigation {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
    width: 100%;
    max-width: 640px;
    min-height: 96px;
    padding: 8px;
    border-radius: 999px;
    background: var(--bg-bottom-menu);
}

.navigation-item {
    display: flex;
    flex: 1 1 0;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
    min-height: 76px;
    padding: 8px;
    border-radius: 999px;
    color: var(--bottom-menu-icon);
    text-decoration: none;
    -webkit-tap-highlight-color: transparent;
}

.navigation-item--active {
    flex-grow: 1.8;
    justify-content: center;
    padding-inline: 12px;
    color: var(--bottom-menu-icon-checked);
    background: rgb(255 255 255 / 14%);
}

.navigation-item__label {
    font-size: 17px;
    font-weight: 650;
    line-height: 1.15;
    white-space: nowrap;
}

.navigation-item__icon {
    display: flex;
    flex: 0 0 40px;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
}

.navigation-item__icon :deep(svg) {
    display: block;
    width: 100%;
    height: 100%;
}

@media (max-width: 480px) {
    .bottom-navigation {
        min-height: 76px;
        padding: 5px;
    }

    .navigation-item {
        min-height: 64px;
        gap: 3px;
        padding: 5px;
    }

    .navigation-item--active {
        padding-inline: 8px;
    }

    .navigation-item__icon {
        flex-basis: 32px;
        width: 32px;
        height: 32px;
    }

    .navigation-item__label {
        font-size: 13px;
    }
}
</style>