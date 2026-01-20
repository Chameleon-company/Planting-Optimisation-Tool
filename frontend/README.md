# Planting Optimisation Tool – Frontend

This folder contains the frontend for the Planting Optimisation Tool.  
It is a multi-page Vite + TypeScript application that provides:

- A **Home** page (Landing page)
- A **Environmental Profile** page
- A **Sapling Calculator** page
- A **Agroforestry Recommendation** page
- A **Species** page

---

## Tech Stack

- **Build tool:** Vite 7 (multi-page setup)
- **Language:** TypeScript (no framework, vanilla TS)
- **Styling:** CSS (global styles in `src/style.css` and page‑specific CSS)
- **Testing / tooling:**
  - Vitest
  - ESLint, Stylelint
  - Prettier

---

## App Structure (High Level)

Key files:

- `index.html` – Home page
- `profile.html` – Environmental Profile page (To be updated)
- `calculator.html` – Sapling Calculator page (To be updated)
- `recommendation.html` - Agroforestry Recommendation page (To be updated)
- `species.html` – Species page (To be updated)

Main TypeScript entry points:

- `src/home.ts` – Home page logic (navigation)
- `src/profile.ts` – Environmental profile generation logic (To be updated)
- `src/calculator.ts` – Sapling Calculator (To be updated)
- `src/recommendation.ts` – Agroforestry Recommendation (To be updated)
- `src/species.ts` – Searching species information based on keywords (To be updated)

Vite is configured in `vite.config.ts` to treat these HTML files as separate entry points.

---

## How to Run the Frontend

From the project root:

```bash
cd Planting-Optimisation-Tool/frontend
npm install
npm run dev
```

## 1. Fork and Clone the repository

First fork the repo to create your own copy:
https://github.com/Chameleon-company/Planting-Optimisation-Tool/fork

Then clone your fork locally

```bash
git clone https://github.com/<your-username>/Planting-Optimisation-Tool.git  # Replace <your-username> with your github username.
cd Planting-Optimisation-Tool
```

Add the project repo as remote to keep your fork up to date

```bash
git remote add upstream https://github.com/Chameleon-company/Planting-Optimisation-Tool.git
git remote -v
```

#### To work on a feature, create a branch for it.

```bash
git checkout -b feature/<feature-name>  # e.g. feature/recommendation-tool
```

Make your changes to what you're working on.

## Before You Commit

A few important points to keep in mind to make sure your contributions are safe, clean, and easy to review:

1. **Never commit secrets or credentials** – do not include API keys, passwords, or `.env` files in your commits. Use environment variables or secret management instead.

2. **Run linting and formatting** – make sure your code follows the project’s style guidelines before committing:

   ```bash
   npm run lint       # frontend
   npm run format     # frontend
   ```

3. **Write clear commit messages** – short but descriptive messages make reviewing and tracking changes easier.

4. **Keep PRs focused** – one feature, bugfix, or documentation change per PR. Avoid unrelated changes.

5. **Sync with the main repository** – regularly pull from `upstream/master` to avoid merge conflicts:

   ```bash
   git fetch upstream
   git checkout master
   git merge upstream/master
   git checkout feature/<branch-name>
   git rebase master
   ```

6. **Don’t commit unnecessary files** – node modules, build artifacts, logs, or temporary IDE files should be ignored (`.gitignore`).

7. **Document important changes** – if your contribution affects setup, usage, or configuration, update the README or other documentation.

8. **Check for sensitive information in comments or logs** – remove passwords, internal URLs, or secret tokens.

9. **Tag the affected team / area in your PR** – Frontend, Backend, Data Science, Documentation, etc., to help reviewers know who should look at it.

Following these guidelines ensures that contributions are safe, consistent, and easy to review.

## 2. When you're ready to commit:

Stage your changes with

```
git add .
```

Then commit your changes with

```bash
git commit -m "Description of changes, what you are committing"
```

Then push your changes **locally** to your fork with

```bash
git push origin feature/<branch-name>
```

# **MOST IMPORTANT - BEFORE SUBMITTING PR**

- Your code **MUST** have tests committed with it.
- Your code **MUST** be documented, legible and following the guidelines.
- Your code **MUST** be linked to an item in the project planner in MS Teams that is assigned to **YOU**.

Failure to adhere to any of the the above will result in your PR **not being accepted**.

Once you have confirmed:

Open a Pull request - https://github.com/Chameleon-company/Planting-Optimisation-Tool/compare

Fill out the PR template and click Create Pull request. Then mark off your task on the MS Teams planner [here](https://teams.microsoft.com/l/entity/com.microsoft.teamspace.tab.planner/_djb2_msteams_prefix_4285208193?context=%7B%22channelId%22%3A%2219%3A040b4a55d7084ae0b2426a200c20ac53%40thread.tacv2%22%7D&tenantId=d02378ec-1688-46d5-8540-1c28b5f470f6).

---

## 3. Front-end setup

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

then to start the development server

```bash
npm run dev
```

If you get errors or white screen after pulling new changes, run `npm install` again to update dependencies.

### Testing

The front end uses **Vitest** for testing

```bash
npm run test # runs tests
npm run test -- --coverage # runs tests with coverage
```

Your code must include tests and pass existing tests before submitting a PR.

The front end uses [ESlint](https://eslint.org/docs/latest/use/getting-started) for linting

```bash
npm run lint:scripts # checks code
npm run lint:styles  # checks css
```

[Prettier](https://prettier.io/docs/) for code formatting

```bash
npm run format:scripts  # format code
npm run format:styles   # format CSS/SCSS
npm run format           # formats everything
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
