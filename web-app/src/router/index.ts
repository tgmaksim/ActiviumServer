import {
    createRouter,
    createWebHistory,
} from "vue-router";

import AppView from "@/views/app/AppView.vue";
import LoginView from "@/views/LoginView.vue";

import ScheduleView from "@/views/tabs/schedule/ScheduleView.vue";
import MarksView from "@/views/tabs/marks/MarksView.vue";
import SchoolView from "@/views/tabs/school/SchoolView.vue";
import SettingsView from "@/views/tabs/settings/SettingsView.vue";

import { routes } from "@/constants/routes";

import { Analytics } from "@/firebase/analytics";

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
                    meta: {
                        analyticsName: "schedule",
                    },
                },
                {
                    path: "marks",
                    name: "marks",
                    component: MarksView,
                    meta: {
                        analyticsName: "marks",
                    },
                },
                {
                    path: "school",
                    name: "school",
                    component: SchoolView,
                    meta: {
                        analyticsName: "school",
                    },
                },
                {
                    path: "settings",
                    name: "settings",
                    component: SettingsView,
                    meta: {
                        analyticsName: "settings",
                    },
                },
            ],
        },
        {
            path: routes.loginBase,
            name: "login",
            component: LoginView,
            meta: {
                analyticsName: "login",
            },
        }
    ],
});

router.afterEach((to, from, failure) => {
    if (failure) {
        return;
    }

    const screenName = String(
        to.meta.analyticsName ?? to.name ?? to.path,
    );

    void Analytics.logScreenView(screenName);
});

export default router;