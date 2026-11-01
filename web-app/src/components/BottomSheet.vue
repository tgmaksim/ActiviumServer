<template>
    <Teleport to="body">
        <Transition name="bottom-sheet">
            <div
                v-if="modelValue"
                class="bottom-sheet-overlay"
                @click.self="close"
            >
                <section
                    class="bottom-sheet-panel"
                    :class="{
                        'bottom-sheet-expanded': isExpanded,
                        'bottom-sheet-dragging': isDragging,
                    }"
                    :style="panelStyle"
                    role="dialog"
                    aria-modal="true"
                    :aria-label="ariaLabel"
                    :aria-labelledby="ariaLabelledby"
                    @click.stop
                >
                    <div
                        class="bottom-sheet-drag-area"
                        aria-hidden="true"
                        @pointerdown="onPointerDown"
                        @pointermove="onPointerMove"
                        @pointerup="onPointerUp"
                        @pointercancel="onPointerCancel"
                    >
                        <div class="bottom-sheet-indicator"></div>
                    </div>

                    <slot
                        name="header"
                        :close="close"
                        :expanded="isExpanded"
                        :toggle-expanded="toggleExpanded"
                    />

                    <div class="bottom-sheet-content">
                        <slot />
                    </div>

                    <slot
                        name="footer"
                        :close="close"
                        :expanded="isExpanded"
                    />
                </section>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import {
    computed,
    onBeforeUnmount,
    ref,
    watch,
} from "vue";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        ariaLabel?: string;
        ariaLabelledby?: string;
        initialExpanded?: boolean;
    }>(),
    {
        ariaLabel: undefined,
        ariaLabelledby: undefined,
        initialExpanded: false,
    },
);

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
    "expanded-change": [expanded: boolean];
}>();

const HISTORY_KEY = "__activiumBottomSheet";

let nextSheetId = 0;

const historyToken = `bottom-sheet-${++nextSheetId}`;

let bodyLockCount = 0;
let previousBodyOverflow = "";

const isExpanded = ref(false);
const isDragging = ref(false);
const dragOffset = ref(0);

let pointerStartY = 0;
let pointerStartTime = 0;
let pointerId: number | null = null;

const panelStyle = computed(() => {
    if (!isDragging.value) {
        return undefined;
    }

    return {
        transform: `translate3d(0, ${dragOffset.value}px, 0)`,
    };
});

/**
 * Блокируем прокрутку фоновой страницы.
 *
 * Счётчик нужен для корректной работы нескольких экземпляров.
 */
function lockBodyScroll(): void {
    if (bodyLockCount === 0) {
        previousBodyOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
    }

    bodyLockCount++;
}

function unlockBodyScroll(): void {
    if (bodyLockCount === 0) {
        return;
    }

    bodyLockCount--;

    if (bodyLockCount === 0) {
        document.body.style.overflow = previousBodyOverflow;
    }
}

/**
 * Добавляем запись в историю браузера.
 *
 * Благодаря этому системный Back сначала закрывает Bottom Sheet,
 * а не выполняет переход на предыдущую страницу.
 */
function addHistoryEntry(): void {
    if (history.state?.[HISTORY_KEY] === historyToken) {
        return;
    }

    const currentState =
        history.state !== null &&
        typeof history.state === "object"
            ? history.state
            : {};

    history.pushState(
        {
            ...currentState,
            [HISTORY_KEY]: historyToken,
        },
        "",
    );
}

/**
 * Убираем временную запись из истории,
 * если закрытие инициировано самим компонентом.
 */
function removeHistoryEntry(): void {
    if (history.state?.[HISTORY_KEY] === historyToken) {
        history.back();
    }
}

/**
 * Обработка системной кнопки Back и жеста браузера.
 */
function onPopState(): void {
    if (!props.modelValue) {
        return;
    }

    if (history.state?.[HISTORY_KEY] !== historyToken) {
        emit("update:modelValue", false);
    }
}

/**
 * Дополнительное закрытие клавишей Escape.
 *
 * Закрывается только верхний Bottom Sheet в истории.
 */
function onKeyDown(event: KeyboardEvent): void {
    if (
        event.key !== "Escape" ||
        history.state?.[HISTORY_KEY] !== historyToken
    ) {
        return;
    }

    event.preventDefault();
    close();
}

function activate(): void {
    isExpanded.value = props.initialExpanded;
    dragOffset.value = 0;
    isDragging.value = false;

    addHistoryEntry();
    lockBodyScroll();

    window.addEventListener("popstate", onPopState);
    document.addEventListener("keydown", onKeyDown);
}

function deactivate(): void {
    window.removeEventListener("popstate", onPopState);
    document.removeEventListener("keydown", onKeyDown);

    unlockBodyScroll();

    removeHistoryEntry();

    isDragging.value = false;
    dragOffset.value = 0;
}

/**
 * Закрытие диалога.
 */
function close(): void {
    if (!props.modelValue) {
        return;
    }

    emit("update:modelValue", false);
}

/**
 * Управление разворачиванием.
 */
function setExpanded(expanded: boolean): void {
    if (isExpanded.value === expanded) {
        return;
    }

    isExpanded.value = expanded;
    emit("expanded-change", expanded);
}

function toggleExpanded(): void {
    setExpanded(!isExpanded.value);
}

/**
 * Начало перетаскивания за индикатор.
 */
function onPointerDown(event: PointerEvent): void {
    if (
        event.pointerType === "mouse" &&
        event.button !== 0
    ) {
        return;
    }

    pointerId = event.pointerId;
    pointerStartY = event.clientY;
    pointerStartTime = performance.now();

    isDragging.value = true;
    dragOffset.value = 0;

    (event.currentTarget as HTMLElement)
        .setPointerCapture(event.pointerId);
}

/**
 * Во время перетаскивания визуально смещаем диалог вниз.
 */
function onPointerMove(event: PointerEvent): void {
    if (
        !isDragging.value ||
        pointerId !== event.pointerId
    ) {
        return;
    }

    dragOffset.value = Math.max(
        0,
        event.clientY - pointerStartY,
    );
}

/**
 * Завершение перетаскивания.
 *
 * Обычное состояние:
 *   свайп вверх — развернуть;
 *   свайп вниз — закрыть.
 *
 * Развёрнутое состояние:
 *   свайп вниз — свернуть.
 */
function onPointerUp(event: PointerEvent): void {
    if (
        !isDragging.value ||
        pointerId !== event.pointerId
    ) {
        return;
    }

    const deltaY = event.clientY - pointerStartY;
    const elapsed = Math.max(
        1,
        performance.now() - pointerStartTime,
    );

    const velocity = deltaY / elapsed;

    isDragging.value = false;
    dragOffset.value = 0;
    pointerId = null;

    if (isExpanded.value) {
        if (
            deltaY > 80 ||
            velocity > 0.55
        ) {
            setExpanded(false);
        }

        return;
    }

    if (
        deltaY < -80 ||
        velocity < -0.55
    ) {
        setExpanded(true);
        return;
    }

    if (
        deltaY > 100 ||
        velocity > 0.65
    ) {
        close();
    }
}

/**
 * Отмена перетаскивания браузером.
 */
function onPointerCancel(event: PointerEvent): void {
    if (pointerId !== event.pointerId) {
        return;
    }

    isDragging.value = false;
    dragOffset.value = 0;
    pointerId = null;
}

watch(
    () => props.modelValue,
    (opened) => {
        if (opened) {
            activate();
        } else {
            deactivate();
        }
    },
    {
        flush: "sync",
        immediate: true,
    },
);

onBeforeUnmount(() => {
    if (props.modelValue) {
        deactivate();
    }
});

defineExpose({
    close,
    toggleExpanded,
    isExpanded,
});
</script>

<style scoped>
.bottom-sheet-overlay {
    position: fixed;
    z-index: 1000;
    inset: 0;

    display: flex;
    align-items: flex-end;
    justify-content: center;

    background: rgb(0 0 0 / 45%);
}

.bottom-sheet-panel {
    display: flex;
    flex-direction: column;

    width: min(100%, 720px);
    height: fit-content;
    max-height: 85vh;
    max-height: 85dvh;
    min-height: 0;

    padding-bottom: max(12px, env(safe-area-inset-bottom));

    overflow: hidden;

    border: 1px solid var(--stroke-bg);
    border-bottom: 0;
    border-radius: 20px 20px 0 0;

    background: var(--main-bg);
    color: var(--text-primary);

    box-sizing: border-box;

    transition:
        transform 280ms cubic-bezier(0.2, 0, 0, 1),
        border-radius 280ms ease;
}

.bottom-sheet-expanded {
    width: 100%;
    height: 100vh;
    height: 100dvh;
    max-height: 100vh;
    max-height: 100dvh;

    padding-top: env(safe-area-inset-top);

    border-radius: 0;
}

.bottom-sheet-dragging {
    transition: none;
}

/* Область захвата жеста */

.bottom-sheet-drag-area {
    display: flex;
    flex: 0 0 28px;
    align-items: center;
    justify-content: center;

    width: 100%;

    cursor: grab;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
}

.bottom-sheet-drag-area:active {
    cursor: grabbing;
}

.bottom-sheet-indicator {
    width: 36px;
    height: 4px;

    border-radius: 4px;

    background: var(--stroke-bg);
}

/* Заголовок и содержимое */

.bottom-sheet-content {
    flex: 1 1 auto;

    width: 100%;
    min-width: 0;
    min-height: 0;

    overflow-x: hidden;
    overflow-y: auto;

    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}

/* Анимация открытия и закрытия */

.bottom-sheet-enter-active,
.bottom-sheet-leave-active {
    transition: opacity 220ms ease;
}

.bottom-sheet-enter-active .bottom-sheet-panel,
.bottom-sheet-leave-active .bottom-sheet-panel {
    transition:
        transform 280ms cubic-bezier(0.2, 0, 0, 1),
        border-radius 280ms ease;
}

.bottom-sheet-enter-from,
.bottom-sheet-leave-to {
    opacity: 0;
}

.bottom-sheet-enter-from .bottom-sheet-panel,
.bottom-sheet-leave-to .bottom-sheet-panel {
    transform: translateY(100%);
}
</style>
