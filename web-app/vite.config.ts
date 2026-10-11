import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from "node:url";
import fs from "node:fs";
import path from "node:path";

const base = "/app/";

const dataPath = path.resolve("config.json");
const data = JSON.parse(fs.readFileSync(dataPath, "utf-8"));

const {
    version,
    versionCode,
    apiDomain,
    checkInternetDomain,
    firebase,
} = data;

export default defineConfig({
    base,

    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },

    define: {
        __APP_VERSION__: JSON.stringify(version),
        __APP_VERSION_CODE__: JSON.stringify(versionCode),
        __API_DOMAIN__: JSON.stringify(apiDomain),
        __CHECK_INTERNET_DOMAIN__: JSON.stringify(checkInternetDomain),

        __FIREBASE_API_KEY__: JSON.stringify(firebase.apiKey),
        __FIREBASE_AUTH_DOMAIN__: JSON.stringify(firebase.authDomain),
        __FIREBASE_PROJECT_ID__: JSON.stringify(firebase.projectId),
        __FIREBASE_STORAGE_BUCKET__: JSON.stringify(firebase.storageBucket),
        __FIREBASE_MESSAGING_SENDER_ID__: JSON.stringify(firebase.messagingSenderId),
        __FIREBASE_APP_ID__: JSON.stringify(firebase.appId),
        __FIREBASE_MEASUREMENT_ID__: JSON.stringify(firebase.measurementId),
        __FIREBASE_VAPID_KEY__: JSON.stringify(firebase.messaging.vapidKey),
    },

    plugins: [
        vue(),

        VitePWA({
            strategies: "injectManifest",
            srcDir: "src",
            filename: "sw.ts",
            registerType: "autoUpdate",

            injectManifest: {
                globPatterns: [
                    "**/*.{js,css,html,ico,png,svg,webp,woff2}",
                ],
            },

            manifest: {
                name: "Активиум — Web-приложение",
                short_name: "Активиум",
                description: "Удобное Web-приложение Активиум — расписание, оценки, мероприятия, рейтинг и статистика — все под рукой!",

                start_url: base,
                scope: base,
                display: "standalone",
                theme_color: "#ffffff",
                background_color: "#ffffff",
                lang: "ru",

                icons: [
                    {
                        src: "/assets/icons/android-chrome-192x192.png",
                        sizes: "192x192",
                        type: "image/png",
                    },
                    {
                        src: "/assets/icons/android-chrome-512x512.png",
                        sizes: "512x512",
                        type: "image/png",
                    },
                    {
                        src: "/assets/icons/apple-touch-icon.png",
                        sizes: "180x180",
                        type: "image/png",
                    },
                    {
                        src: "/assets/icons/favicon-16x16.png",
                        sizes: "16x16",
                        type: "image/png",
                    },
                    {
                        src: "/assets/icons/favicon-32x32.png",
                        sizes: "32x32",
                        type: "image/png",
                    },
                    {
                        src: "/assets/icons/favicon.ico",
                        sizes: "48x48",
                        type: "image/x-icon",
                    },
                ],
            },
        }),
    ],
});