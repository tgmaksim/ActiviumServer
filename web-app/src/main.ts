import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import { launch } from "./bootstrap/launcher";
import "./style.css";

if (launch()) {
    const app = createApp(App);

    app.use(createPinia());

    app.mount("#app");
}