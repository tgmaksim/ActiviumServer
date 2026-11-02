export interface HeartPoint {
    x: number;
    y: number;
}

function isInsideHeart(x: number, y: number): boolean {
    const value = Math.pow(
        x * x + y * y - 1,
        3,
    ) - x * x * Math.pow(y, 3);

    return value <= 0;
}

export function generateHeartPoints(
    count: number,
    centerX: number,
    centerY: number,
    scale: number,
): HeartPoint[] {
    const points: HeartPoint[] = [];

    let attempts = 0;
    const maxAttempts = count * 100;

    while (
        points.length < count &&
        attempts < maxAttempts
    ) {
        attempts++;

        const x = Math.random() * 2.4 - 1.2;
        const y = Math.random() * 2.4 - 1.2;

        if (!isInsideHeart(x, y)) {
            continue;
        }

        points.push({
            x: centerX + x * scale,
            y: centerY - y * scale,
        });
    }

    return points;
}