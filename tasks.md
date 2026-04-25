# Task Breakdown

> **Source:** This task breakdown is derived from [`prd.md`](./prd.md).

## Project Summary

This project is a **whitelabel university library chatbot MVP**. Students use natural language to search for books in their university library. The chatbot returns the top-ranked results as cards (title, author, year) with a map feature showing each book's physical location inside the library. An admin dashboard lets library staff manage books, maps, and per-university UI customization (colors, logos). The MVP showcases Anhembi Morumbi university, but the architecture supports multi-tenant deployment (e.g., `ucla.our-library.com`). The AI pipeline is based on the [TranslateMyPrompt](https://deepwiki.com/Karina-Lima/TransalteMyPrompt) project architecture.

---

## 1. Backend — AI Agents (Flask)

- [ ] **1.1** Set up the Flask project structure, virtual environment, and base configuration (environment variables, CORS, logging).
- [ ] **1.2** Implement the **Professor Agent** — receives the student's natural-language query and produces four essential subjects related to the topic.
- [ ] **1.3** Implement the **Researcher Agent** — takes the four subjects and the selected format filters (books, comics/HQs, journals) and returns five candidate books.
- [ ] **1.4** Implement the **Educator Agent** — generates a short synopsis for each candidate book.
- [ ] **1.5** Implement the **Descriptive Agent** — fetches additional metadata from the internet (Amazon) for each candidate book.
- [ ] **1.6** Build the **orchestrator pipeline** that chains Professor → Researcher → Educator → Descriptive and exposes the result through a single REST endpoint. Reference the TranslateMyPrompt project architecture for the agent-chaining pattern.

## 2. Backend — Admin CRUD (Flask)

- [ ] **2.1** Create CRUD endpoints for **books and map data** (add, edit, delete, list books; upload/update library map and book locations).
- [ ] **2.2** Create CRUD endpoints for **UI configuration** (university logo, primary/secondary colors, custom labels).
- [ ] **2.3** Implement **multi-tenant URL routing** so each university is served under its own subdomain (e.g., `anhembi.our-library.com`, `ucla.our-library.com`), loading the correct configuration per tenant.

## 3. Backend — Authentication

- [ ] **3.1** Implement **student authentication** — login/register flow that grants access to the chatbot interface.
- [ ] **3.2** Implement **admin authentication** — login flow that grants access to the admin dashboard.
- [ ] **3.3** Implement **role-based access control (RBAC)** to enforce that students can only access the chatbot and admins can only access the dashboard.

## 4. Frontend — Student UI (React)

- [ ] **4.1** Set up the React project (bundler, routing, global styles, folder structure).
- [ ] **4.2** Build the **chat input component** — text field for natural-language queries with a send button.
- [ ] **4.3** Build the **filter checkboxes** — allow students to filter by book type (HQs, books, journals).
- [ ] **4.4** Build the **loading state** — display a loading indicator while the AI pipeline processes the request.
- [ ] **4.5** Build the **book result cards** — display the top three books, each showing title, author, year, and a "See Map" button.
- [ ] **4.6** Build the **map feature** — when "See Map" is clicked, show the book's specific location and the route from the library entrance.
- [ ] **4.7** Implement **dynamic theming** — apply colors, logo, and labels from the admin-configured UI settings so each university sees its own branding.

## 5. Frontend — Admin Dashboard (React)

- [ ] **5.1** Build the **admin login page** with credential form and error handling.
- [ ] **5.2** Build the **dashboard layout** — sidebar navigation, header with university name/logo, and content area.
- [ ] **5.3** Build the **book management panel** — table/list view to add, edit, and delete books.
- [ ] **5.4** Build the **map management panel** — upload/update the library map and set book locations.
- [ ] **5.5** Build the **UI customization panel** — form to update university logo, color scheme, and custom labels with a live preview.

## 6. Integration & Rules

- [ ] **6.1** **Brazilian Portuguese localization** — all student-facing and admin-facing UI text must be written in Brazilian Portuguese.
- [ ] **6.2** **Dynamic theming enforcement** — the chatbot UI must follow the colors and logos configured in the admin dashboard at all times.
- [ ] **6.3** **Google Books API integration** — use the Google Books API as the primary data source for book searches in the Researcher Agent.
- [ ] **6.4** **Amazon metadata integration** — use Amazon as the source for additional book metadata in the Descriptive Agent.
- [ ] **6.5** **Mock data for MVP** — since this is an MVP showcasing Anhembi Morumbi, provide mock/seed data for books, map, and UI configuration so the demo works end-to-end without requiring a full production setup.
