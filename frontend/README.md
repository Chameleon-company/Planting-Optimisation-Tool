# Planting Optimisation Tool – Frontend

This folder contains the frontend for the Planting Optimisation Tool.  
It is a multi-page Vite + TypeScript application that provides:

- A **Home** page (Landing page)
- An **Environmental Profile** page
- A **Sapling Calculator** page
- An **Agroforestry Recommendation** page
- A **Species** page

---

## Tech Stack

- **Build tool:** Vite 7
- **Language:** TypeScript
- **Framework:** React 19
- **Styling:** CSS (global styles in `src/style.css`)
- **Testing / tooling:**
  - Vitest + React Testing Library
  - ESLint, Stylelint
  - Prettier

---

## App Structure (High Level)

Key files:

- `index.html` – Single HTML entry point
- `src/main.tsx` – React app entry point
- `src/App.tsx` – Root component, routing, and error boundary

Source structure:

- `src/components/` – Reusable UI components grouped by feature
- `src/pages/` – Top level page components
- `src/hooks/` – Custom React hooks
- `src/contexts/` – React Context providers
- `src/errors/` – Error boundary components
- `src/utils/` – Utility functions and API clients
- `src/test/` – Vitest + React Testing Library test files

---

## Frontend Setup

The front-end is built with React. Make sure you have **Node.js (v24+)** and **npm** installed.

[Download Node.js](https://nodejs.org/en/download)

Confirm installation with:

```bash
node -v # should return >24.0
npm -v
```

then

```bash
cd frontend
npm install # to install dependencies
```

---

## How to Run the Frontend

From the project root:

```bash
cd Planting-Optimisation-Tool/frontend
npm run dev
```

If you get errors or white screen after pulling new changes, run `npm install` again to update dependencies.

---

## Contributing

For repository contribution workflow, branching, commit guidelines, PR requirements, and general development practices, refer to the root [CONTRIBUTING.md](../CONTRIBUTING.md).

---

### Testing

The frontend uses **Vitest** for testing

```bash
npm run test # runs tests
npm run test -- --coverage # runs tests with coverage
```

Your changes should include appropriate tests for the affected module and all existing tests must pass before submitting a PR.

Testing standards and coverage expectations are documented in the project Test Strategy document.

The frontend uses [ESLint](https://eslint.org/docs/latest/use/getting-started) for linting

```bash
npm run lint:scripts  # checks code
npm run lint:styles   # checks css
```

[Prettier](https://prettier.io/docs/) for code formatting

```bash
npm run format:scripts  # format code
npm run format:styles   # format CSS/SCSS
npm run format          # formats everything
```

[Husky](https://github.com/typicode/husky) is set up for pre-commit hooks. When you commit, lint-staged will run to ensure your staged files are properly linted and formatted. You do not need to run it manually.

---

## Useful NPM Scripts

From the `frontend` directory:

- `npm run dev` – start the Vite dev server
- `npm run build` – build the production bundle into `build/dist`
- `npm run test` / `npm run test:coverage` – run unit tests with Vitest
- `npm run lint:scripts` – lint TypeScript files with ESLint
- `npm run lint:styles` – lint CSS/SCSS with Stylelint
- `npm run format` – format scripts and styles with Prettier + Stylelint

## Contentful SDK for CMS of Species Information

This project uses [Contentful](https://www.contentful.com/) as a headless CMS to store and retrieve **Species Information**, including fields:

- Name
- Scientific Name
- Description
- Keywords
- Image

This enables easy keyword searching and displays the relevant species information cards in the Species page.

## Configuration

1. Create a `.env` file in the `frontend/` directory.

2. Add the required environment variables to the `.env` file:

```env
VITE_SPACE_ID=
VITE_ACCESS_TOKEN=
```
Please check the secure handover notes for these credentials
