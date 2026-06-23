const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

document.documentElement.style.setProperty(
    '--tg-theme-bg-color',
    tg.themeParams.bg_color || '#ffffff'
);

document.documentElement.style.setProperty(
    '--tg-theme-secondary-bg-color',
    tg.themeParams.secondary_bg_color || '#f5f7fb'
);

document.documentElement.style.setProperty(
    '--tg-theme-text-color',
    tg.themeParams.text_color || '#111827'
);

document.documentElement.style.setProperty(
    '--tg-theme-hint-color',
    tg.themeParams.hint_color || '#6b7280'
);

document.documentElement.style.setProperty(
    '--tg-theme-link-color',
    tg.themeParams.link_color || '#2563eb'
);

document.documentElement.style.setProperty(
    '--tg-theme-button-color',
    tg.themeParams.button_color || '#2481cc'
);

document.documentElement.style.setProperty(
    '--tg-theme-button-text-color',
    tg.themeParams.button_text_color || '#ffffff'
);