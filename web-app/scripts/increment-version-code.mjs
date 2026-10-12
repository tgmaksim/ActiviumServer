import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, "..");
const dataPath = path.join(
    projectRoot,
    "config.json",
);

const data = JSON.parse(
    await readFile(dataPath, "utf-8"),
);

data.versionCode++;

await writeFile(
    dataPath,
    JSON.stringify(data, null, 4) + "\n",
);

console.log(`APP_VERSION_CODE = ${data.versionCode}`);