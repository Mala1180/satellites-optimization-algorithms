import cors from "cors";
import express from 'express';
import fs from 'fs';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

const app = express();
const port = 3000;
const __dirname = dirname(fileURLToPath(import.meta.url));

app.use(cors());
app.use(express.static('tools/instance_viewer'));
app.get('/', (req, res) => {
    res.sendFile('viewer.html', { root: path.join(__dirname, './tools/instance_viewer') });
});

app.get('/instances/', async (req, res) => {
    const result = (await fs.promises.readdir('./instances/', { withFileTypes: true }))
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
    res.json(result);
});

app.get('/instances/:name/dtos', (req, res) => {
    const instanceName = req.params.name;
    fs.readFile(`./instances/${instanceName}/DTOs.json`, "utf8", (err, jsonString) => {
        if (err) {
            res.status(500).send("File read failed:", err);
            console.log("File read failed:", err);
            return;
        }
        else {
            res.json(JSON.parse(jsonString));
        }
    });
});


app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})
