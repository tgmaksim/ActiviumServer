import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dist = path.join(__dirname, "dist");

const projectRoot = path.resolve(__dirname, "..");

const templates = path.join(projectRoot, "templates");
const staticApp = path.join(projectRoot, "www", "app");

await mkdir(templates, { recursive: true });

await rm(path.join(templates, "app.html"), { force: true });
await rm(staticApp, { recursive: true, force: true });

await mkdir(staticApp, { recursive: true });

// index.html → templates/app.html
await cp(
    path.join(dist, "index.html"),
    path.join(templates, "app.html"),
);

// Всё кроме index.html → www/app
await cp(dist, staticApp, {
    recursive: true,
    filter: (source) => !source.endsWith(`${path.sep}index.html`),
});

console.log("Vue application copied to FastAPI.");