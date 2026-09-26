import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
    base: "/app/",

    resolve: {
        alias: {
          '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },

    plugins: [
        vue(),

        VitePWA({
            registerType: "autoUpdate",

            manifest: {
                name: "Активиум - Web приложение для школы",
                short_name: "Активиум",
                description: "Удобное Web приложение Активиум — расписание, оценки, мероприятия, рейтинг и статистика — все под рукой!",

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