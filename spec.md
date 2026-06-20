# spec.md - RAG PDF Chapter Splitter (Functional Specifications)

## 1. Product Overview
The system is a local-first, privacy-centric application designed to parse, contextualize, and split PDF books into individual chapters. Its primary goal is to generate clean, highly specific PDF chunks to optimize indexing and eliminate hallucinations in downstream RAG systems (e.g., NotebookLM). The architecture features a FastAPI Python backend and a minimalist Next.js frontend.

## 2. Core Workflows & Features

### 2.1 Secure Credentials Management (The Vault)
* **Objective:** Securely store and manage user API keys (OpenAI, Google Drive, etc.) without exposing them in plaintext.
* **Requirements:**
  * The backend must generate a local `.vault.key` file automatically on first boot if it does not exist.
  * All API keys entered via the UI must be encrypted using AES-256-GCM before being stored in the SQLite database.
  * The frontend will provide a dedicated "Settings" view to add, update, or mask existing API keys.
  * The system must operate seamlessly after the initial key generation without requiring the user to input master passwords.

### 2.2 The PDF Extraction Engine (Dual Path System)
* **Objective:** Accurately detect and split chapters from any technical or standard PDF book.
* **Requirements:**
  * **Path A (Metadata/Happy Path):** The system must first attempt to read embedded Table of Contents (TOC) metadata using PyMuPDF. If valid metadata exists, it will use this to accurately split the pages mathematically.
  * **Path B (AI-Assisted/Complex Path):** If no metadata exists, the system will extract the first 15-20 pages and route them to the configured AI engine (Local Ollama or External API). The AI must return a strict JSON payload mapping chapter numbers, titles, and start/end page coordinates.

### 2.3 Context Injection
* **Objective:** Enhance RAG semantic search capabilities.
* **Requirements:**
  * During the splitting process, the system must programmatically inject a small context block on the first page of every separated PDF.
  * Format: "Context: This document is Chapter [X] of the book [Book Title]. Subject: [Topic]."

### 2.4 Handling of "Extra" Content
* **Objective:** Preserve non-chapter reference material systematically.
* **Requirements:**
  * Front matter (Cover, TOC, Foreword) must be separated and saved as a distinct file (e.g., `00 - Front Matter`).
  * Back matter (Glossary, Index, Appendices) must be grouped and saved after the final chapter (e.g., `99 - Appendices`).

### 2.5 Storage Routing & Auto-Structuring
* **Objective:** Automatically organize output files in the user's preferred environment.
* **Requirements:**
  * The user must be able to select between Local Storage or Google Drive Storage.
  * The system must automatically generate a parent folder named after the book.
  * Output file naming convention must be strictly enforced: `[Book Name] - [Chapter ##] - [Chapter Title].pdf`.
  * Filenames must be sanitized to prevent OS-level path or saving errors.

### 2.6 Library Management (CRUD)
* **Objective:** Allow the user to manage their processed library.
* **Requirements:**
  * The Next.js UI must display a list of all processed books and their associated chapters retrieved from the SQLite database.
  * Users can edit the title of a book or specific chapters to correct minor AI parsing errors.
  * Users can delete a book record. Deleting a book must offer a toggle to simultaneously wipe the generated files from the local disk or Google Drive to prevent orphaned data.

### 2.7 User Interface (UI)
* **Objective:** Provide a fast, native-feeling GUI.
* **Requirements:**
  * Aesthetic must be minimalist, high-contrast, utilizing 1px borders, dot-matrix subtle accents, and glassmorphism.
  * No heavy branding; focus entirely on typography, usability, and technical precision.
