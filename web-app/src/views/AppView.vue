<template>
    <div class="app-layout">
        <main class="app-content">
            <RouterView v-slot="{ Component }">
                <KeepAlive>
                    <component :is="Component" />
                </KeepAlive>
            </RouterView>
        </main>

        <Toast />

        <footer class="app-footer">
            <BottomNavigation />
        </footer>
    </div>
</template>

<script setup lang="ts">
import BottomNavigation from "@/components/BottomNavigation.vue";
import Toast from "@/components/Toast.vue";
</script>

<style scoped>
.app-layout {
    min-height: 100vh;
    min-height: 100dvh;
    background: var(--main-bg);
}

.app-content {
    min-width: 0;
    min-height: 100vh;
    min-height: 100dvh;
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