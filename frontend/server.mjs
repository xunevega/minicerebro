import { createServer } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL(".", import.meta.url)), "dist");
const port = Number.parseInt(process.env.PORT || "4173", 10);
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".webmanifest": "application/manifest+json",
};

function securityHeaders(cacheControl) {
  return {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy":
      "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self'; connect-src 'self' https://*.up.railway.app http://127.0.0.1:* http://localhost:*",
    "Cache-Control": cacheControl,
  };
}

function sendFile(res, filePath, cacheControl) {
  const stream = createReadStream(filePath);
  res.writeHead(200, {
    "Content-Type": types[extname(filePath)] || "application/octet-stream",
    ...securityHeaders(cacheControl),
  });
  stream.pipe(res);
}

const server = createServer((req, res) => {
  const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
  const safePath = normalize(urlPath).replace(/^(\.\.[/\\])+/, "");
  const filePath = join(root, safePath);
  const hashedAsset = /\/assets\/.+\.[a-zA-Z0-9_-]{8,}\.(js|css)$/.test(safePath);
  const cacheControl = hashedAsset ? "public, max-age=31536000, immutable" : "no-cache";

  if (existsSync(filePath) && statSync(filePath).isFile()) {
    sendFile(res, filePath, cacheControl);
    return;
  }

  sendFile(res, join(root, "index.html"), "no-cache");
});

server.listen(port, "0.0.0.0", () => {
  process.stdout.write(`Editados frontend on ${port}\n`);
});
