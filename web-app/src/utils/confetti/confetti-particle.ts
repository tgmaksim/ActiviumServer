export interface ConfettiParticleOptions {
    image: HTMLCanvasElement;

    startX: number;
    startY: number;

    targetX: number;
    targetY: number;

    size: number;
    delay: number;
    duration: number;

    holdDuration: number;
    fadeDuration: number;

    arcOffset: number;
}

function clamp(
    value: number,
    min: number,
    max: number,
): number {
    return Math.max(min, Math.min(max, value));
}

function easeOutCubic(value: number): number {
    return 1 - Math.pow(1 - value, 3);
}

export class ConfettiParticle {
    private readonly image: HTMLCanvasElement;

    private readonly startX: number;
    private readonly startY: number;

    private readonly targetX: number;
    private readonly targetY: number;

    private readonly size: number;

    private readonly delay: number;
    private readonly duration: number;

    private readonly holdDuration: number;
    private readonly fadeDuration: number;

    private readonly arcOffset: number;

    private readonly directionX: number;
    private readonly directionY: number;

    private startTime = 0;

    constructor(options: ConfettiParticleOptions) {
        this.image = options.image;

        this.startX = options.startX;
        this.startY = options.startY;

        this.targetX = options.targetX;
        this.targetY = options.targetY;

        this.size = options.size;

        this.delay = options.delay;
        this.duration = options.duration;

        this.holdDuration = options.holdDuration;
        this.fadeDuration = options.fadeDuration;

        this.arcOffset = options.arcOffset;

        const dx = this.targetX - this.startX;
        const dy = this.targetY - this.startY;

        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            this.directionX = -dy / distance;
            this.directionY = dx / distance;
        } else {
            this.directionX = 0;
            this.directionY = 0;
        }
    }

    draw(
        ctx: CanvasRenderingContext2D,
        now: number,
    ): boolean {
        if (this.startTime === 0) {
            this.startTime = now;
        }

        const elapsed = now - this.startTime;

        const lifetime =
            this.delay +
            this.duration +
            this.holdDuration +
            this.fadeDuration;

        if (elapsed >= lifetime) {
            return false;
        }

        const movementTime = Math.max(
            0,
            elapsed - this.delay,
        );

        const progress = clamp(
            movementTime / this.duration,
            0,
            1,
        );

        const easedProgress = easeOutCubic(progress);

        const arc = Math.sin(
            progress * Math.PI,
        ) * this.arcOffset;

        const x =
            this.startX +
            (this.targetX - this.startX) * easedProgress +
            this.directionX * arc;

        const y =
            this.startY +
            (this.targetY - this.startY) * easedProgress +
            this.directionY * arc;

        const fadeStart =
            this.delay +
            this.duration +
            this.holdDuration;

        const fadeProgress = clamp(
            (elapsed - fadeStart) / this.fadeDuration,
            0,
            1,
        );

        const alpha = 1 - fadeProgress;

        const scale =
            0.75 +
            0.25 * Math.sin(progress * Math.PI);

        const size = this.size * scale;

        ctx.globalAlpha = alpha;

        ctx.drawImage(
            this.image,
            x - size / 2,
            y - size / 2,
            size,
            size,
        );

        ctx.globalAlpha = 1;

        return true;
    }
}