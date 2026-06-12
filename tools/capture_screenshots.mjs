import { access, mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const FRONTEND_URL =
  process.env.CRISOL_FRONTEND_URL
  ?? "https://crisol-web.jollysmoke-c46778ba.eastus.azurecontainerapps.io";
const BACKEND_URL =
  process.env.CRISOL_BACKEND_URL
  ?? "https://crisol-api.jollysmoke-c46778ba.eastus.azurecontainerapps.io";
const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const outputDirectory = path.resolve(
  scriptDirectory,
  "../docs/assets/screenshots",
);
const warnings = [];

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  console.error(
    "Playwright is not installed. Run: npm install --prefix tools && "
    + "npm exec --prefix tools playwright install chromium",
  );
  process.exit(1);
}

await mkdir(outputDirectory, { recursive: true });

async function fetchJson(route, init) {
  const response = await fetch(`${BACKEND_URL}${route}`, {
    headers: { Accept: "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`${route} returned HTTP ${response.status}`);
  }
  return response.json();
}

async function saveJson(name, value) {
  await writeFile(
    path.join(outputDirectory, name),
    `${JSON.stringify(value, null, 2)}\n`,
    "utf8",
  );
}

async function fileExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function capture(page, name) {
  await page.screenshot({
    path: path.join(outputDirectory, name),
    fullPage: true,
  });
  console.log(`Captured ${name}`);
}

async function openFrontend(page) {
  await page.goto(FRONTEND_URL, {
    waitUntil: "domcontentloaded",
    timeout: 60_000,
  });
  await page.getByRole("navigation", { name: "Product sections" })
    .waitFor({ state: "visible", timeout: 30_000 });
  await page.getByText("Loading command center...")
    .waitFor({ state: "hidden", timeout: 30_000 })
    .catch(() => {});
}

async function openSection(page, label, screenshotName) {
  const navigationButton = page.getByRole("button", {
    name: label,
    exact: true,
  });
  if (await navigationButton.count() !== 1) {
    warnings.push(`Could not find section navigation: ${label}`);
    await capture(page, screenshotName);
    return false;
  }
  await navigationButton.click();
  await page.getByRole("heading", { name: label, exact: false })
    .waitFor({ state: "visible", timeout: 15_000 })
    .catch(() => {});
  await capture(page, screenshotName);
  return true;
}

const health = await fetchJson("/health");
const groundingStatus = await fetchJson("/grounding/status");
let workspaceStatus = await fetchJson("/workspace/status");

await saveJson("backend-health.json", health);
await saveJson("grounding-status.json", groundingStatus);

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  colorScheme: "dark",
  deviceScaleFactor: 1,
  viewport: { width: 1600, height: 1000 },
});
const page = await context.newPage();

try {
  await openFrontend(page);

  if (workspaceStatus.is_empty) {
    await capture(page, "01-empty-workspace.png");
    console.log("Applying Creator Operations Readiness to the empty workspace.");
    await fetchJson("/workspace/apply-template/template-creator-operations", {
      method: "POST",
    });
    workspaceStatus = await fetchJson("/workspace/status");
    if (workspaceStatus.is_empty) {
      warnings.push("Creator Operations Readiness did not configure the workspace.");
    }
    await page.reload({ waitUntil: "domcontentloaded", timeout: 60_000 });
    await page.getByText("Loading command center...")
      .waitFor({ state: "hidden", timeout: 30_000 })
      .catch(() => {});
  } else {
    const emptyCapture = path.join(outputDirectory, "01-empty-workspace.png");
    if (!await fileExists(emptyCapture)) {
      await capture(page, "01-empty-workspace.png");
      warnings.push(
        "The production workspace was already configured; "
        + "01-empty-workspace.png shows the current workspace.",
      );
    }
  }

  await openSection(page, "Command Center", "00-command-center.png");
  await openSection(page, "Workspace Setup", "02-workspace-setup.png");
  await openSection(page, "Scenario Studio", "03-scenario-studio.png");

  const evaluationOpened = await openSection(
    page,
    "Evaluation Room",
    "04-evaluation-room.png",
  );
  if (evaluationOpened) {
    const runButton = page.getByRole("button", {
      name: "Run Evaluation",
      exact: true,
    });
    if (await runButton.count() === 1 && await runButton.isEnabled()) {
      await runButton.click();
      await page.getByRole("button", {
        name: "View Full Results",
        exact: true,
      }).waitFor({ state: "visible", timeout: 60_000 }).catch(() => {
        warnings.push("The synthetic evaluation did not finish before capture.");
      });
      await capture(page, "04-evaluation-room.png");
    } else {
      warnings.push("Run Evaluation was unavailable; captured the ready state.");
    }
  }

  await openSection(page, "Results Center", "05-results-center.png");
  await openSection(page, "Tools & Readiness", "06-tools-readiness.png");

  await page.setContent(`
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>CRISOL Grounding Status</title>
        <style>
          :root { color-scheme: dark; }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #03090d;
            color: #dce7ec;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
          }
          main {
            width: min(960px, calc(100vw - 80px));
            border: 1px solid #27414b;
            border-radius: 8px;
            background: #071016;
            padding: 40px;
            box-shadow: 0 24px 80px rgba(0, 0, 0, .45);
          }
          p { margin: 0; color: #67e8f9; font-size: 13px; text-transform: uppercase; }
          h1 { margin: 10px 0 8px; font-size: 36px; letter-spacing: 0; }
          .endpoint { color: #71858f; font-family: ui-monospace, monospace; font-size: 13px; }
          pre {
            margin: 28px 0 0;
            overflow: auto;
            border-left: 3px solid #34d399;
            background: #02070a;
            padding: 24px;
            color: #a7f3d0;
            font: 16px/1.7 ui-monospace, SFMono-Regular, Consolas, monospace;
          }
        </style>
      </head>
      <body>
        <main>
          <p>Live production API</p>
          <h1>CRISOL Grounding Status</h1>
          <div class="endpoint">${escapeHtml(BACKEND_URL)}/grounding/status</div>
          <pre>${escapeHtml(JSON.stringify(groundingStatus, null, 2))}</pre>
        </main>
      </body>
    </html>
  `);
  await capture(page, "07-grounding-status.png");
} finally {
  await browser.close();
}

if (warnings.length) {
  await writeFile(
    path.join(outputDirectory, "capture-warnings.txt"),
    `${warnings.join("\n")}\n`,
    "utf8",
  );
  console.warn(warnings.join("\n"));
} else {
  await writeFile(
    path.join(outputDirectory, "capture-warnings.txt"),
    "No capture warnings.\n",
    "utf8",
  );
}

console.log(`Screenshots saved to ${outputDirectory}`);
