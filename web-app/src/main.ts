import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

import { launch } from "./bootstrap/launcher";
import { initializeSW } from "./utils/register-sw";
import "./style.css";

import { Utilities } from "@/utils/utils";

import { createPinia } from "pinia";
import { useSettingsStore } from "@/stores/settings";
import { initializeTheme } from "@/theme/theme-manager";

const initialRoute = launch();

initializeSW();

const app = createApp(App);

const pinia = createPinia()
app.use(pinia);
useSettingsStore(pinia);

initializeTheme();

app.use(router);

app.mount("#app");

router.isReady().then(() => {
    if (initialRoute !== null && router.currentRoute.value.path !== initialRoute) {
        router.replace(initialRoute);
    }
});