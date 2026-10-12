import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

import { launch } from "./bootstrap/launcher";
import "./style.css";

const initialRoute = launch();

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");

router.isReady().then(() => {
    if (router.currentRoute.value.path !== initialRoute) {
        router.replace(initialRoute);
    }
});