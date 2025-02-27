const express = require('express');
const app = express();
const port = 3000;
const path = require('path');
const fs = require('fs'); // استيراد fs لقراءة ملفات النظام

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/api/course', (req, res) => {
    // قراءة ملف JSON بشكل متزامن
    fs.readFile(path.join(__dirname, 'csvjson.json'), 'utf8', (err, data) => {
        if (err) {
            return res.status(500).json({ error: 'حدث خطأ أثناء قراءة بيانات الكورسات.' });
        }
        const courses = JSON.parse(data); // تحويل البيانات إلى JSON
        res.json(courses); // إرجاع بيانات الكورسات
    });
});

app.get('/:page', (req, res) => {
    const pagePath = path.join(__dirname, 'public', 'html', req.params.page);
    res.sendFile(pagePath, (err) => {
        if (err) {
            res.status(404).send("الصفحة غير موجودة!");
        }
    });
});

// تشغيل السيرفر
app.listen(port, () => {
    console.log(`API is running on http://localhost:${port}`);
});
