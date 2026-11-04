<template>
    <div class="app-layout">
        <main class="app-content">
            <RouterView v-slot="{ Component }">
                <KeepAlive>
                    <component :is="Component" />
                </KeepAlive>
            </RouterView>
        </main>

        <ConfettiCanvas />

        <Toast />

        <footer class="app-footer">
            <BottomNavigation />
        </footer>
    </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, provide } from "vue";
import { useRoute } from "vue-router";

import BottomNavigation from "@/components/BottomNavigation.vue";
import Toast from "@/components/Toast.vue";
import ConfettiCanvas from "@/components/ConfettiCanvas.vue";

import { AppViewModel, appViewModelKey } from "@/views/app/app-view-model";

// Единый экземпляр ViewModel для всего приложения.
const appViewModel = new AppViewModel();

provide(appViewModelKey, appViewModel);

const route = useRoute();

// Отслеживание возвращения приложения из фонового режима.
let wasHidden = false;

/**
 * Обрабатывает изменение видимости приложения.
 */
function handleVisibilityChange(): void {
    if (document.visibilityState === "hidden") {
        wasHidden = true;

        appViewModel.pauseStudy();

        return;
    }

    if (wasHidden) {
        wasHidden = false;

        appViewModel.checkAccessibleAd();
        appViewModel.checkStudy(() => route.name);
    }
}

onMounted(() => {
    document.addEventListener(
        "visibilitychange",
        handleVisibilityChange,
    );

    // Первоначальная проверка рекламы.
    appViewModel.checkAccessibleAd();

    // Первоначальная проверка обучающих подсказок.
    appViewModel.checkStudy(() => route.name);
});

onBeforeUnmount(() => {
    document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange,
    );

    appViewModel.pauseStudy();
});
</script>

<style scoped>
.app-layout {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    background: var(--main-bg);
}

.app-content {
    flex: 1 1 0;
    width: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
}

.app-footer {
    position: fixed;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 1000;

    display: flex;
    justify-content: center;

    width: 100%;
    box-sizing: border-box;
    padding: 8px 12px max(8px, env(safe-area-inset-bottom));

    pointer-events: none;
}

.app-footer :deep(.bottom-navigation) {
    width: 100%;
    max-width: 480px;
    pointer-events: auto;
}
</style>