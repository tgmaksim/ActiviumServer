import { createApp } from "vue";
import { createPinia } from "pinia";

import AppView from "./views/AppView.vue";
import router from "./router";

import { launch } from "./bootstrap/launcher";
import "./style.css";

const initialRoute = launch();

const app = createApp(AppView);

app.use(createPinia());
app.use(router);

app.mount("#app");

router.isReady().then(() => {
    if (router.currentRoute.value.path !== initialRoute) {
        router.replace(initialRoute);
    }
});