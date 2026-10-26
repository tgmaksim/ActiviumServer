<template>
    <div class="app-layout">
        <main class="app-content">
            <RouterView v-slot="{ Component }">
                <KeepAlive>
                    <component :is="Component" />
                </KeepAlive>
            </RouterView>
        </main>

        <footer class="app-footer">
            <BottomNavigation />
        </footer>
    </div>
</template>

<script setup lang="ts">
import BottomNavigation from "@/components/BottomNavigation.vue";
</script>

<style scoped>
.app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    min-height: 100dvh;
    background: var(--main-bg);
}

.app-content {
    flex: 1;
    min-width: 0;
    padding: 24px;
}

.app-footer {
    display: flex;
    justify-content: center;
    width: 100%;
    padding: 16px 24px 20px;
}

@media (max-width: 600px) {
    .app-content {
        padding: 20px 16px;
    }

    .app-footer {
        position: sticky;
        bottom: 0;
        z-index: 10;
        padding: 8px 12px max(8px, env(safe-area-inset-bottom));
        background: var(--main-bg);
    }

    .app-footer :deep(.bottom-navigation) {
        max-width: none;
    }
}
</style>