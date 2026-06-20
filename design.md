# design.md - Ripper Architecture & UI Guidelines

## 1. High-Level Architecture
Ripper operates on a decoupled, local-first Client-Server architecture designed for absolute privacy and high-performance processing.

* **Frontend (Presentation Layer):** Next.js application running on `localhost`. Responsible for rendering the UI, capturing user configurations, and managing state via React Hooks.
* **Backend (Application & Processing Layer):** FastAPI (Python) server. Exposes a RESTful API to the frontend. Handles PDF manipulation (`PyMuPDF`), cryptographic operations (`cryptography`), and routes extraction tasks to the AI Engine (local Ollama or external endpoints).
* **Data Layer (Persistence & Security):** SQLite local database. Stores the AES-256-GCM encrypted API keys and the library inventory (books and separated chapters).
* **File System (I/O):** Local OS file system and Google Drive API integration for directory creation and PDF output storage.

## 2. System Communication Flow
1.  **Boot Sequence:** FastAPI backend starts, checks for `.vault.key`, generates it if missing, and loads the master key into RAM.
2.  **UI Initialization:** Next.js frontend mounts and fetches the current library state via `GET /api/books`.
3.  **Authentication/Settings:** User inputs an API key in the UI -> Frontend sends `POST /api/config` -> Backend encrypts the payload using the master key -> Stores encrypted blob in SQLite.
4.  **Processing Pipeline:**
    * User uploads PDF via UI -> Frontend sends `POST /api/process` with file and user preferences (AI model, storage destination).
    * Backend executes Path A (Metadata TOC) or Path B (AI Extraction).
    * Backend splits the PDF, injects context, and saves chunks to the selected destination.
    * Backend updates SQLite with the new book and chapter records.
    * Backend returns a 200 OK with the new library state to the frontend.

## 3. UI/UX Visual Guidelines (The Aesthetic)
The frontend must strictly adhere to a "Nothing/Apple" inspired minimalist design language. It should feel like a premium, native piece of hardware engineering—utilitarian, sharp, and stripped of unnecessary ornamentation.

### 3.1 Color Palette (High-Contrast Monochromatic)
* **Background:** True Black (`#000000`) for Dark Mode / Pure White (`#FFFFFF`) for Light Mode.
* **Surface:** Very subtle off-black (`#0A0A0A`) or off-white (`#FAFAFA`) for cards/modals.
* **Text (Primary):** `#FFFFFF` (Dark Mode) / `#000000` (Light Mode).
* **Text (Secondary/Muted):** `#888888` (for hints, metadata, and disabled states).
* **Borders:** `#333333` (Dark) / `#E5E5E5` (Light).
* **Accents:** Only use colors for critical states (e.g., `#FF4444` for destructive actions like deleting a book, `#00C853` for success).

### 3.2 Typography
* **Primary Font:** `Inter` or system-native `San Francisco`. Use geometric, clean weights (Regular 400 for body, Medium 500 for buttons, SemiBold 600 for headings).
* **Monospaced Font:** `JetBrains Mono` or `Fira Code`. Strictly reserved for API keys, terminal-like logs, progress outputs, and chapter coordinates.

### 3.3 Component Styling & Structural Rules
* **Borders:** Strictly 1px solid lines. Avoid thick or dashed borders.
* **Border Radius:** Subtle rounding (`rounded-md` or `rounded-lg` in Tailwind, approx 6px-8px). Do not use pill-shaped or overly circular buttons unless it's a specific toggle switch.
* **Shadows & Depth:** Avoid flat drop-shadows. Use *Glassmorphism* (backdrop-blur) for floating elements, dropdowns, and confirmation modals to create depth without relying on solid shadows.
* **Dot-Matrix Accents:** Use a faint SVG dot-matrix pattern for the background of empty states (e.g., when the library is empty) or header sections to evoke an industrial, hardware-like feel.
* **Micro-interactions:** * Buttons should have a fast, subtle opacity or scale transition on hover (`transition-all duration-200 ease-in-out`).
    * Skeleton loaders should be used instead of standard spinning wheels for data fetching.

### 3.4 Accessibility (a11y)
* **Contrast Ratios:** Ensure text and interactive elements meet WCAG AA standards.
* **Keyboard Navigation:** All menus, buttons, and settings must be fully navigable via the `Tab` key with clear focus rings (`focus:ring-1 focus:ring-white`).
* **Aria Labels:** Any icon-only buttons (like a trash can for deletion or a gear for settings) must have descriptive `aria-label` tags.
