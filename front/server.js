import express from "express";
import { render } from "./dist/server/entry-server.js"; // тут поправил путь

const app = express();

// Отдаём собранный клиентский код
app.use(express.static("dist/client", { index: false }));

app.get("/legal", async (req, res) => {
    const { appHtml, legal } = await render();

    res.send(`
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>Legal</title>
      </head>
      <body>
        <div id="root">${appHtml}</div>
        <script>
          window.__INITIAL_DATA__ = ${JSON.stringify(legal)};
        </script>
        <script type="module" src="/entry-client.js"></script>
      </body>
    </html>
    `);
});

app.listen(3000, () => {
    console.log("SSR server running at http://localhost:3000/legal");
});