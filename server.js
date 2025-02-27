const port = process.env.PORT || 3000;
import express from 'express';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';

// ✅ تعريف __filename و __dirname أولًا
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express(); // ✅ تعريف التطبيق بعد __dirname

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// استدعاء ملف JSON من Gist
const jsonUrl = "https://gist.githubusercontent.com/m7md1221/0a092a379eae0d060d3049131bacc8ad/raw/a5c4e9ddb2a881a6a531028216222ebfdf3d8d97/data.json";

app.get('/api/course', async (req, res) => {
    try {
        const response = await fetch(jsonUrl);
        console.log("استجابة Gist:", response.status, response.statusText);
        
        if (!response.ok) throw new Error('فشل تحميل البيانات');

        const courses = await response.json();
        res.json(courses);
    } catch (error) {
        console.error("❌ خطأ في جلب البيانات:", error);
        res.status(500).json({ error: 'حدث خطأ أثناء جلب بيانات الكورسات.' });
    }
});

app.get('/:page', (req, res) => {
    const pagePath = path.join(__dirname, 'public', 'html', req.params.page);
    res.sendFile(pagePath, (err) => {
        if (err) {
            res.status(404).send("الصفحة غير موجودة!");
        }
    });
});

app.listen(port, () => {
    console.log(`API is running on http://localhost:${port}`);
});
