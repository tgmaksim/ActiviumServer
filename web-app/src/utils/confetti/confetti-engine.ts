import {
    ConfettiParticle,
} from "./confetti-particle";

import {
    generateHeartPoints,
} from "./confetti-heart";

import type {
    ConfettiParticleOptions,
} from "./confetti-particle";

export interface ConfettiOptions {
    x?: number;
    y?: number;
    particleCount?: number;
}

type ConfettiPalette = [
    string,
    string,
    string,
];

const DEFAULT_PALETTE: ConfettiPalette = [
    "#0288D1",
    "#4FC3F7",
    "#80DEEA",
];

const MIN_PARTICLE_SIZE = 19;
const MAX_PARTICLE_SIZE = 29;

const PARTICLE_COUNT = 110;

const MOVEMENT_DURATION_MIN = 850;
const MOVEMENT_DURATION_MAX = 1150;

const HOLD_DURATION = 450;
const FADE_DURATION = 800;

const MAX_DEVICE_PIXEL_RATIO = 2.5;

const iconModules = import.meta.glob<string>(
    "@/assets/konfetti/*.svg",
    {
        eager: true,
        query: "?url",
        import: "default",
    },
);

const iconUrls = Object.entries(iconModules)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, url]) => url);

function randomBetween(
    min: number,
    max: number,
): number {
    return min + Math.random() * (max - min);
}

function getPalette(): ConfettiPalette {
    const styles = getComputedStyle(
        document.documentElement,
    );

    const getColor = (
        variable: string,
        fallback: string,
    ): string => {
        return (
            styles.getPropertyValue(variable).trim() ||
            fallback
        );
    };

    return [
        getColor(
            "--praise-particle-primary",
            DEFAULT_PALETTE[0],
        ),
        getColor(
            "--praise-particle-secondary",
            DEFAULT_PALETTE[1],
        ),
        getColor(
            "--praise-particle-accent",
            DEFAULT_PALETTE[2],
        ),
    ];
}

function loadImage(
    url: string,
): Promise<HTMLImageElement | null> {
    return new Promise((resolve) => {
        const image = new Image();

        image.onload = () => resolve(image);
        image.onerror = () => resolve(null);

        image.src = url;
    });
}

function tintImage(
    image: HTMLImageElement,
    color: string,
): HTMLCanvasElement {
    const canvas = document.createElement("canvas");

    canvas.width = image.naturalWidth || 64;
    canvas.height = image.naturalHeight || 64;

    const ctx = canvas.getContext("2d");

    if (!ctx) {
        return canvas;
    }

    ctx.drawImage(
        image,
        0,
        0,
        canvas.width,
        canvas.height,
    );

    ctx.globalCompositeOperation = "source-in";
    ctx.fillStyle = color;

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height,
    );

    ctx.globalCompositeOperation = "source-over";

    return canvas;
}

export class ConfettiEngine {
    private readonly canvas: HTMLCanvasElement;

    private ctx: CanvasRenderingContext2D | null = null;

    private width = 0;
    private height = 0;
    private pixelRatio = 1;

    private icons: HTMLImageElement[] = [];

    private tintedIcons = new Map<
        string,
        HTMLCanvasElement[]
    >();

    private particles: ConfettiParticle[] = [];

    private pendingStarts: ConfettiOptions[] = [];

    private animationFrame = 0;

    private initialized = false;
    private destroyed = false;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
    }

    async initialize(): Promise<void> {
        this.ctx = this.canvas.getContext("2d", {
            alpha: true,
        });

        if (!this.ctx) {
            return;
        }

        this.resize();

        window.addEventListener(
            "resize",
            this.resize,
            { passive: true },
        );

        const loadedIcons = await Promise.all(
            iconUrls.map(loadImage),
        );

        if (this.destroyed) {
            return;
        }

        this.icons = loadedIcons.filter(
            (image): image is HTMLImageElement =>
                image !== null,
        );

        if (this.icons.length === 0) {
            console.error(
                "[Confetti] Не удалось загрузить SVG-иконки.",
            );

            return;
        }

        this.initialized = true;

        const pending = this.pendingStarts.splice(0);

        pending.forEach((options) => {
            this.startNow(options);
        });
    }

    start(options: ConfettiOptions = {}): void {
        if (this.destroyed) {
            return;
        }

        if (!this.initialized) {
            this.pendingStarts.push(options);
            return;
        }

        this.startNow(options);
    }

    private startNow(options: ConfettiOptions): void {
        if (!this.ctx || this.icons.length === 0) {
            return;
        }

        const centerX = Number.isFinite(options.x)
            ? options.x!
            : this.width / 2;

        const centerY = Number.isFinite(options.y)
            ? options.y!
            : this.height / 2;

        const particleCount = Math.max(
            24,
            Math.min(
                120,
                Math.round(
                    options.particleCount ?? PARTICLE_COUNT,
                ),
            ),
        );

        const palette = getPalette();
        const tintedIcons = this.getTintedIcons(palette);

        if (tintedIcons.length === 0) {
            return;
        }

        const scale = Math.min(
            this.width * 0.42,
            this.height * 0.38,
        );

        const heartCenterX = Math.max(
            scale * 1.2,
            Math.min(
                this.width - scale * 1.2,
                centerX,
            ),
        );

        const heartCenterY = Math.max(
            scale * 1.3,
            Math.min(
                this.height - scale * 1.3,
                centerY,
            ),
        );

        const targets = generateHeartPoints(
            particleCount,
            heartCenterX,
            heartCenterY,
            scale,
        );

        const particles = targets.map((target) => {
            const imageSet =
                tintedIcons[
                    Math.floor(
                        Math.random() * tintedIcons.length,
                    )
                ];

            const image =
                imageSet[
                    Math.floor(
                        Math.random() * imageSet.length,
                    )
                ];

            const particleOptions: ConfettiParticleOptions = {
                image,

                startX: centerX,
                startY: centerY,

                targetX: target.x,
                targetY: target.y,

                size: randomBetween(
                    MIN_PARTICLE_SIZE,
                    MAX_PARTICLE_SIZE,
                ),

                delay: randomBetween(0, 140),

                duration: randomBetween(
                    MOVEMENT_DURATION_MIN,
                    MOVEMENT_DURATION_MAX,
                ),

                holdDuration: HOLD_DURATION,
                fadeDuration: FADE_DURATION,

                arcOffset: randomBetween(-28, 28),
            };

            return new ConfettiParticle(
                particleOptions,
            );
        });

        this.particles.push(...particles);

        this.startRendering();
    }

    private getTintedIcons(
        palette: ConfettiPalette,
    ): HTMLCanvasElement[][] {
        return palette.map((color) => {
            const cached = this.tintedIcons.get(color);

            if (cached) {
                return cached;
            }

            const images = this.icons.map((image) =>
                tintImage(image, color),
            );

            this.tintedIcons.set(color, images);

            return images;
        });
    }

    private resize = (): void => {
        this.width = window.innerWidth;
        this.height = window.innerHeight;

        this.pixelRatio = Math.min(
            window.devicePixelRatio || 1,
            MAX_DEVICE_PIXEL_RATIO,
        );

        this.canvas.width = Math.round(
            this.width * this.pixelRatio,
        );

        this.canvas.height = Math.round(
            this.height * this.pixelRatio,
        );

        this.ctx?.setTransform(
            this.pixelRatio,
            0,
            0,
            this.pixelRatio,
            0,
            0,
        );
    };

    private startRendering(): void {
        if (this.animationFrame !== 0) {
            return;
        }

        this.animationFrame = requestAnimationFrame(
            this.render,
        );
    }

    private render = (now: number): void => {
        const ctx = this.ctx;

        if (!ctx || this.destroyed) {
            this.animationFrame = 0;
            return;
        }

        ctx.clearRect(
            0,
            0,
            this.width,
            this.height,
        );

        for (
            let i = this.particles.length - 1;
            i >= 0;
            i--
        ) {
            const particle = this.particles[i];

            const alive = particle.draw(ctx, now);

            if (!alive) {
                this.particles.splice(i, 1);
            }
        }

        if (this.particles.length > 0) {
            this.animationFrame = requestAnimationFrame(
                this.render,
            );
        } else {
            this.animationFrame = 0;
        }
    };

    destroy(): void {
        this.destroyed = true;

        window.removeEventListener(
            "resize",
            this.resize,
        );

        if (this.animationFrame !== 0) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = 0;
        }

        this.particles = [];
        this.pendingStarts = [];

        this.icons = [];
        this.tintedIcons.clear();

        this.ctx?.clearRect(
            0,
            0,
            this.width,
            this.height,
        );

        this.ctx = null;
        this.initialized = false;
    }
}