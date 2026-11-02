import {
    ConfettiEngine,
    type ConfettiOptions,
} from "@/utils/confetti/confetti-engine";

let activeEngine: ConfettiEngine | null = null;

export function registerConfettiEngine(
    engine: ConfettiEngine,
): () => void {
    activeEngine = engine;

    return () => {
        if (activeEngine === engine) {
            activeEngine = null;
        }
    };
}

export function useConfetti() {
    function startConfettiAnimation(
        options: ConfettiOptions = {},
    ): void {
        activeEngine?.start(options);
    }

    return {
        startConfettiAnimation,
    };
}