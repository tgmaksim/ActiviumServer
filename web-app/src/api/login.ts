import { routes } from "../constants/routes";

interface LoginUrlResponse {
    loginUrl: string;
}

export async function getLoginUrl(): Promise<string> {
    const response = await fetch(routes.loginUrl, {
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error(`Failed to get login URL: ${response.status}`);
    }

    const data = await response.json() as LoginUrlResponse;

    return data.loginUrl;
}