import { cpSync, existsSync, mkdirSync } from "node:fs";
import { watch } from "chokidar";
import path from "node:path";

const SRC = path.resolve("data/templates/dyad");
const DST = path.resolve("data/templates/_active");

if (!existsSync(SRC)) mkdirSync(SRC, { recursive: true });
if (!existsSync(DST)) mkdirSync(DST, { recursive: true });

function syncAll() {
  cpSync(SRC, DST, { recursive: true });
  console.log("[dyad-sync] synced", new Date().toLocaleTimeString());
}
syncAll();
watch(SRC, { ignoreInitial: true }).on("all", syncAll);
