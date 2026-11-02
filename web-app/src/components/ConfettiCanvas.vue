<script setup lang="ts">
import {
    onBeforeUnmount,
    onMounted,
    ref,
} from "vue";

import {
    ConfettiEngine,
} from "@/utils/confetti/confetti-engine";

import {
    registerConfettiEngine,
} from "@/composables/useConfetti";


const canvasRef = ref<HTMLCanvasElement | null>(null);

let engine: ConfettiEngine | null = null;
let unregister: (() => void) | null = null;


onMounted(() => {
    const canvas = canvasRef.value;

    if (!canvas) {
        return;
    }

    engine = new ConfettiEngine(canvas);

    unregister = registerConfettiEngine(engine);

    void engine.initialize();
});


onBeforeUnmount(() => {
    unregister?.();
    unregister = null;

    engine?.destroy();
    engine = null;
});
</script>

<template>
    <canvas
        ref="canvasRef"
        class="confetti-canvas"
        aria-hidden="true"
    />
</template>

<style scoped>
.confetti-canvas {
    position: fixed;
    inset: 0;
    z-index: 9999;

    display: block;

    width: 100vw;
    height: 100dvh;

    pointer-events: none;
}
</style>