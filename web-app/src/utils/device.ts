export function getDeviceInfo(): string {
    const userAgent = navigator.userAgent;

    let os = "Activium";

    if (/Windows NT/i.test(userAgent)) {
        os = "Windows";
    } else if (/Android/i.test(userAgent)) {
        os = "Android";
    } else if (/iPhone|iPad|iPod/i.test(userAgent)) {
        os = "iOS";
    } else if (/Mac OS X/i.test(userAgent)) {
        os = "macOS";
    } else if (/Linux/i.test(userAgent)) {
        os = "Linux";
    }

    let browser = "Web-приложение";

    if (/Edg\//i.test(userAgent)) {
        browser = "Microsoft Edge";
    } else if (/OPR\//i.test(userAgent)) {
        browser = "Opera";
    } else if (/Firefox\//i.test(userAgent)) {
        browser = "Firefox";
    } else if (/CriOS\//i.test(userAgent)) {
        browser = "Chrome";
    } else if (/Chrome\//i.test(userAgent)) {
        browser = "Chrome";
    } else if (/Safari\//i.test(userAgent)) {
        browser = "Safari";
    }

    return `${os} · ${browser}`;
}