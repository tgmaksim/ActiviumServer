<template>
    <main class="login-page">
        <div class="login-content">
            <!-- Логотип -->
            <img
                class="login-logo"
                :src="`${routes.home}icons/logo.png`"
                :alt="strings.appName"
            />

            <!-- Название -->
            <h1 class="login-title">
                {{ strings.appName }}
            </h1>

            <!-- Описание -->
            <div class="login-about">
                <p>
                    {{ strings.hello }}
                </p>
            </div>

            <!-- Версия и устройство -->
            <div class="login-info">
                <div class="login-version">
                    {{ strings.version(appVersion, appVersionCode) }}
                </div>

                <div class="login-device">
                    {{ deviceInfo }}
                </div>

                <div class="login-developer">
                    {{ strings.developer }}
                </div>
            </div>

            <!-- Согласие с документами -->
            <label class="login-consent">
                <input
                    v-model="acceptedDocuments"
                    type="checkbox"
                    class="login-consent-checkbox"
                />

                <span>
                    Я согласен с
                    <a :href="routes.privacy" target="_blank" rel="noopener noreferrer">
                        Политикой конфиденциальности
                    </a>
                    и
                    <a :href="routes.terms" target="_blank" rel="noopener noreferrer">
                        Условиями пользования
                    </a>
                </span>
            </label>

            <!-- Кнопка -->
            <button
                class="login-button"
                type="button"
                :disabled="loading || !acceptedDocuments"
                @click="login"
            >
                <img
                    class="dnevnik-logo"
                    :src="`${routes.home}icons/dnevnik_ru.svg`"
                    alt=""
                />

                <span>
                    {{ strings.loginWithDnevnik }}
                </span>

                <span
                    v-if="loading"
                    class="login-spinner"
                    aria-label="Загрузка"
                ></span>
            </button>

            <p v-if="error" class="login-error">
                {{ error }}
            </p>
        </div>
    </main>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { routes } from "../constants/routes";
import { strings } from "../constants/strings";

import {
    APP_VERSION,
    APP_VERSION_CODE,
} from "../constants/app";
import { getLoginUrl } from "../api/login";
import { getDeviceInfo } from "../utils/device";

const appVersion = ref(APP_VERSION);
const appVersionCode = ref(APP_VERSION_CODE);

const deviceInfo = getDeviceInfo();

const loading = ref(false);
const acceptedDocuments = ref(true);
const error = ref<string | null>(null);

async function login() {
    if (loading.value || !acceptedDocuments.value) {
        return;
    }

    loading.value = true;
    error.value = null;

    try {
        const loginUrl = await getLoginUrl();

        window.location.href = loginUrl;
    } catch {
        error.value = "Не удалось получить ссылку для авторизации.";
        loading.value = false;
    }
}
</script>

<style scoped>
.login-page {
    min-height: 100vh;
    min-height: 100dvh;

    margin-top: env(safe-area-inset-top, 0);

    background: var(--main-bg);
    color: var(--text-primary);

    overflow-y: auto;
}

.login-content {
    width: 100%;
    max-width: 480px;
    min-height: 100vh;
    min-height: 100dvh;

    margin: 0 auto;
    padding: 30px 24px 24px;

    display: flex;
    flex-direction: column;
    align-items: center;
}

.login-logo {
    width: 120px;
    height: 120px;

    margin-top: 0;

    object-fit: cover;

    border-radius: 50%;
}

.login-title {
    margin: 16px 0 0;

    font-size: 28px;
    line-height: 1.2;
    font-weight: 700;
}

.login-about,
.login-info {
    width: 100%;

    background: var(--bg-login-about);

    border: 1px solid var(--stroke-bg);
    border-radius: 20px;
}

.login-about {
    margin-top: 24px;
    padding: 5px;
}

.login-about p {
    margin: 0;

    font-size: 16px;
    line-height: 1.5;
    font-style: italic;
    text-align: center;
}

.login-info {
    margin-top: 16px;
    padding: 14px;
}

.login-version {
    font-size: 14px;
    line-height: 1.4;
}

.login-device,
.login-developer {
    margin-top: 4px;

    color: var(--text-secondary);

    font-size: 13px;
    line-height: 1.4;
}

.login-consent {
    width: 100%;

    margin-top: 20px;
    padding: 0 4px;

    display: flex;
    align-items: flex-start;
    gap: 10px;

    color: var(--text-secondary);

    font-size: 13px;
    line-height: 1.5;

    cursor: pointer;
}

.login-consent-checkbox {
    width: 18px;
    height: 18px;

    margin: 1px 0 0;

    flex: 0 0 18px;

    accent-color: var(--accent);
    cursor: pointer;
}

.login-consent a {
    color: var(--accent);

    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 2px;
}

.login-consent a:hover {
    opacity: 0.8;
}

.login-button {
    width: 100%;
    min-height: 52px;

    margin-top: 16px;
    padding: 12px;

    display: flex;
    align-items: center;

    border: 0;
    border-radius: 14px;

    background: var(--button-bg);
    color: var(--text-primary);

    font: inherit;
    font-size: 16px;

    text-align: left;

    cursor: pointer;
}

.login-button:disabled {
    cursor: default;
    opacity: 0.5;
}

.dnevnik-logo {
    width: 24px;
    height: 24px;

    flex: 0 0 24px;

    object-fit: contain;
}

.login-button span:not(.login-spinner) {
    margin-left: 12px;
}

.login-spinner {
    width: 25px;
    height: 25px;

    margin-left: auto;

    border: 3px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;

    animation: login-spinner 0.7s linear infinite;
}

.login-error {
    width: 100%;

    margin: 12px 0 0;

    color: var(--settings-warning);

    font-size: 14px;
    text-align: center;
}

@keyframes login-spinner {
    to {
        transform: rotate(360deg);
    }
}
</style>