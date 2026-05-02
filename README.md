# 🤖 Personal AI Agent

بيجاوب على أي سؤال عنك بناءً على الـ CV بتاعك، GitHub، وLinkedIn.

---

## 🗂️ هيكل المشروع

```
personal-ai-agent/
├── main.py                  # نقطة البداية
├── requirements.txt
├── .env.example             # انسخه لـ .env وملأه
├── src/
│   ├── cv_loader.py         # بيقرأ الـ CV (PDF)
│   ├── github_fetcher.py    # بيجيب داتا GitHub تلقائي
│   ├── linkedin_loader.py   # بيقرأ LinkedIn export
│   └── rag_chain.py         # الـ AI + vector store
└── data/                    # حط ملفاتك هنا
    ├── cv.pdf
    └── linkedin_export.zip  # أو مجلد linkedin_export/
```

---

## ⚙️ الإعداد خطوة بخطوة

### 1. تثبيت المتطلبات

```bash
cd personal-ai-agent
pip install -r requirements.txt
```

### 2. إعداد الـ .env

```bash
cp .env.example .env
```

افتح `.env` وملأ:

```env
GROQ_API_KEY=sk-...         # من console.groq.com
GITHUB_TOKEN=ghp_...          # اتفضل الخطوة الجاية
GITHUB_USERNAME=yourusername
YOUR_NAME=Ahmed Mohamed        # اسمك بالكامل
```

### 3. GitHub Token

1. روح: https://github.com/settings/tokens
2. اضغط **Generate new token (classic)**
3. اختار صلاحية: `public_repo` و `read:user`
4. انسخ الـ token وحطه في الـ `.env`

### 4. الـ CV

حط ملف الـ PDF في:
```
data/cv.pdf
```

### 5. LinkedIn Export

1. روح **LinkedIn > Settings & Privacy > Data Privacy**
2. اختار **Get a copy of your data**
3. اختار: Profile, Positions, Education, Skills, Certifications
4. هيجيلك email فيه ZIP خلال 24 ساعة
5. حط الـ ZIP في:
   ```
   data/linkedin_export.zip
   ```

---

## 🚀 التشغيل

```bash
python main.py
```

### أوامر مفيدة

| الأمر | الوظيفة |
|-------|---------|
| `python main.py` | تشغيل عادي |
| `python main.py --rebuild` | إعادة بناء الـ vector store (لو عدلت ملفاتك) |
| `خروج` أو `exit` | للخروج |

---

## 💬 أمثلة على الأسئلة

```
سؤالك: ما هي المهارات التقنية لديك؟
سؤالك: اشرح مشاريع GitHub بتاعتك
سؤالك: ما هي خبرتك في Python؟
سؤالك: What technologies do you work with?
سؤالك: كم سنة خبرة عندك في الـ backend؟
سؤالك: Tell me about your education
```

---

## 🔧 استكشاف الأخطاء

**❌ `GROQ_API_KEY` error**
→ تأكد إن الـ key صح في `.env`

**❌ GitHub 401 Unauthorized**
→ الـ token منتهي أو غلط، اعمل واحد جديد

**❌ مفيش داتا اتحملت**
→ تأكد إن الملفات موجودة في مجلد `data/`

**❌ الإجابات بتيجي غلط**
→ شغّل `python main.py --rebuild` عشان يعيد بناء الـ vector store

---

## 🧠 كيف بيشتغل

```
CV (PDF) ──┐
           │
GitHub ────┼──► Text Chunks ──► Embeddings ──► FAISS Vector Store
           │                                         │
LinkedIn ──┘                                         │
                                                     ▼
                                    سؤالك ──► Retriever ──► GPT-4o-mini ──► الإجابة
```

1. **Data Loading**: بيقرأ الـ CV، يجيب GitHub API، يقرأ LinkedIn CSV
2. **Chunking**: بيقطع الـ text لـ chunks صغيرة
3. **Embedding**: بيحول كل chunk لـ vector رقمي
4. **FAISS**: بيحفظ الـ vectors للبحث السريع
5. **RAG**: لما تسأل، بيجيب أقرب chunks ويديهم للـ GPT يجاوب
