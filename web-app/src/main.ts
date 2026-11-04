import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

import { launch } from "./bootstrap/launcher";
import { initializeSW } from "./utils/register-sw";
import "./style.css";

import { createPinia } from "pinia";
import { useSettingsStore } from "@/stores/settings";
import { initializeTheme } from "@/theme/theme-manager";

import { Analytics } from "@/firebase/analytics";
import { APP_VERSION } from "@/constants/app";

const initialRoute = launch();

initializeSW();

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);
useSettingsStore(pinia);

void Analytics.isAnalyticsSupported().then((supported) => {
    if (!supported) {
        return;
    }

    void Analytics.setAnalyticsDefaultEventParameters({
        app_platform: "web",
        activium_version: APP_VERSION,
    });
});

initializeTheme();

app.use(router);

app.mount("#app");

router.isReady().then(() => {
    if (initialRoute !== null && router.currentRoute.value.path !== initialRoute) {
        router.replace(initialRoute);
    }
});