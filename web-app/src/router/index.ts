import {
    createRouter,
    createWebHistory,
} from "vue-router";

import AppView from "@/views/AppView.vue";
import LoginView from "@/views/LoginView.vue";

import ScheduleView from "@/views/tabs/ScheduleView.vue";
import MarksView from "@/views/tabs/MarksView.vue";
import SchoolView from "@/views/tabs/SchoolView.vue";
import SettingsView from "@/views/tabs/settings/SettingsView.vue";

import { routes } from "@/constants/routes";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),

    routes: [
        {
            path: routes.homeBase,
            component: AppView,
            children: [
                {
                    path: "",
                    name: "schedule",
                    component: ScheduleView,
                },
                {
                    path: "marks",
                    name: "marks",
                    component: MarksView,
                },
                {
                    path: "school",
                    name: "school",
                    component: SchoolView,
                },
                {
                    path: "settings",
                    name: "settings",
                    component: SettingsView,
                },
            ],
        },
        {
            path: routes.loginBase,
            name: "login",
            component: LoginView,
        }
    ],
});

export default router;