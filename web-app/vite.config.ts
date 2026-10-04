import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from 'node:url'
import fs from "node:fs";
import path from "node:path";

const versionPath = path.resolve(
    "version.json",
);

const data = JSON.parse(
    fs.readFileSync(versionPath, "utf-8"),
);
const version = data.version;
const versionCode = data.versionCode;

export default defineConfig({
    base: "/app/",

    resolve: {
        alias: {
          '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },

    define: {
        __APP_VERSION__: JSON.stringify(version),
        __APP_VERSION_CODE__: JSON.stringify(versionCode),
    },

    plugins: [
        vue(),

        VitePWA({
            registerType: "autoUpdate",

            workbox: {
                navigateFallback: "/app",
                navigateFallbackDenylist: [
                    /^\/app\/auth/,
                ],
            },

            manifest: {
                name: "Активиум — Web-приложение",
                short_name: "Активиум",
                description: "Удобное Web-приложение Активиум — расписание, оценки, мероприятия, рейтинг и статистика — все под рукой!",

                start_url: "/app/",
                scope: "/app/",

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