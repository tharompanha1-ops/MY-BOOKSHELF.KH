# 📚 MY BOOKSHELF.KH

**Your Personal Digital Learning Library**

MY BOOKSHELF.KH is an educational platform that organizes learning resources,
books, and study materials in one place. It gives students convenient access to
educational content across different grade levels and subjects — with a clean,
modern, responsive interface and light/dark themes.

## ✨ Features

- 📖 **Digital Library** — Browse and download educational books and PDFs.
- 🎓 **Grade-Based Learning** — Materials organized by grade level (7–12).
- 📚 **Subject Collection** — Browse resources by individual subject.
- 🤖 **AI Chat** — An AI-powered assistant for learning help.
- 🧮 **Unit Converter** — A full unit-conversion tool.
- 📉 **Graphing Calculator** — Plot functions and solve equations.
- 🌗 **Light & Dark Mode** — Automatic theme with a manual toggle.
- 📱 **Fully Responsive** — Mobile, tablet, laptop, desktop, and large screens.
- ♿ **Accessible** — Skip link, focus states, semantic landmarks, ARIA.

## 📁 Project Structure

```text
MY-BOOKSHELF.KH/
├── index.html              # Home page
├── library.html            # Main digital library
├── newspage.html           # News / updates
├── contactpage.html        # Contact form (secure API)
├── converter.html          # Unit converter tool
├── graphing.html           # Graphing calculator tool
├── privacypolicy.html
├── termsofservice.html
├── GradeList/              # Grade 7–12 landing pages
│   └── grade{7..12}.html
├── SubjectList-07..12/     # Subject book pages per grade
│   └── {english,khmer,math,science,media,...}.html
├── src/                    # TypeScript source
│   ├── app.ts              # Shared browser behaviour
│   └── contact.ts          # Serverless contact endpoint
├── assets/
│   ├── css/
│   │   ├── style.css       # Shared design system (all pages)
│   │   └── pages/          # Per-page extracted CSS
│   └── js/
│       └── app.js          # Compiled from src/app.ts (shared behaviour)
├── api/
│   └── contact.js          # Compiled from src/contact.ts (env-based secrets)
├── tools/
│   ├── rebuild.py          # Rebuild processor (rewires pages to shared assets)
│   ├── check_links.py      # Broken internal link checker (report-only)
│   └── link_manifest.py    # Snapshot of all <a href> values
└── tests/
    └── test_rebuild.py     # Integrity + preservation tests
```

## 🛠️ Technologies

**TypeScript** for all shared logic, compiled to plain JavaScript — no framework.
Shared design tokens and behaviour live in `src/` (TypeScript) and are compiled
to `assets/`; each page links the compiled output and keeps only its own
page-specific CSS.

### TypeScript source
```text
src/
├── app.ts        # Shared browser behaviour (compiled -> assets/js/app.js)
└── contact.ts    # Serverless contact endpoint (compiled -> api/contact.js)
```

### Build
```bash
npm install        # installs typescript + @types/node
npm run build      # compiles src/ -> assets/js/app.js and api/contact.js
npm run dev        # watch-build the browser script
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tharompanha1-ops/MY-BOOKSHELF.KH.git
```

### 2. Open the project

```bash
cd MY-BOOKSHELF.KH
```

### 3. Run locally

This is a static site — serve the folder with any static server:

```bash
# Python
python3 -m http.server 8000

# or Node
npx serve .
```

Open `http://localhost:8000` in your browser.

## 🔐 Contact Form & Telegram

The contact form posts to `api/contact.js` (compiled from `src/contact.ts`),
a serverless function that forwards messages to Telegram. **Credentials are
never stored in client code.** Set these environment variables in your
deployment platform:

| Variable              | Description                          |
| --------------------- | ------------------------------------ |
| `TELEGRAM_BOT_TOKEN`  | Bot token from [@BotFather](https://t.me/botfather) |
| `TELEGRAM_CHAT_ID`    | Target chat / channel id             |

Deploy `api/contact.mjs` as a serverless function (Vercel, Netlify,
Cloudflare, etc.) at the `/api/contact` route.

## 🧪 Testing & Link Checks

```bash
# Integrity + preservation tests
python3 tests/test_rebuild.py

# Check for broken internal links (report-only, never rewrites links)
python3 tools/check_links.py

# Re-run the rebuild processor (after editing assets)
python3 tools/rebuild.py
```

The test suite enforces the project's **preservation rule**: every original
`<a href>` destination must survive the rebuild untouched.

## 🎯 Project Goals

- Make educational resources easier to access.
- Organize books and learning materials.
- Support independent learning.
- Provide a convenient, modern digital learning environment.

## 📄 License

This project is provided for educational and personal learning purposes.
All materials remain the property of their respective owners.
