import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, "..");
const versionPath = path.join(
    projectRoot,
    "version.json",
);

const data = JSON.parse(
    await readFile(versionPath, "utf-8"),
);

data.versionCode++;

await writeFile(
    versionPath,
    JSON.stringify(data, null, 4) + "\n",
);

console.log(`APP_VERSION_CODE = ${data.versionCode}`);