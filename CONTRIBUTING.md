# Contributing to the Planting Optimisation Tool

Thank you for your interest in contributing to the **Planting Optimisation Tool**.

This guide explains how to set up your local environment, make changes, and submit a pull request.

---

## Repository Overview

The repository contains multiple areas of the product:

- Frontend
- Backend
- GIS
- Data Science

Before making changes, review the setup documentation for the area you plan to work on.

Setup guides:

- Frontend - https://github.com/Chameleon-company/Planting-Optimisation-Tool/tree/master/frontend#how-to-run-the-frontend
- Backend - https://github.com/Chameleon-company/Planting-Optimisation-Tool/tree/master/backend#getting-started
- Data Science - https://github.com/Chameleon-company/Planting-Optimisation-Tool/blob/master/datascience/README.md
- GIS - https://github.com/Chameleon-company/Planting-Optimisation-Tool/tree/master/gis/docs

---


## 1. Fork and Clone the repository

Fork the repository to create your own copy:
https://github.com/Chameleon-company/Planting-Optimisation-Tool/fork

Clone your fork to your local development environment:
```bash
git clone https://github.com/<your-username>/Planting-Optimisation-Tool.git  # Replace <your-username> with your github username.
cd Planting-Optimisation-Tool
```
Add the project repo as remote (upstream) to keep your fork up to date with the project repository
```bash
git remote add upstream https://github.com/Chameleon-company/Planting-Optimisation-Tool.git
git remote -v
git fetch upstream
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
   npm run lint             # frontend
   npm run format           # frontend
   uv run ruff check --fix       # backend / Data Science / GIS
   uv run ruff format            # backend / Data Science / GIS
   ```  

3. **Write clear commit messages** – short but descriptive messages make reviewing and tracking changes easier.  

4. **Keep PRs focused** – one feature, bugfix, or documentation change per PR. Try to avoid unrelated changes.

5. **Sync with the main repository** – regularly fetch from `upstream/master` to avoid merge conflicts:  
   ```bash
   git fetch upstream
   git checkout master
   git merge upstream/master
   git checkout feature/<branch-name>
   git rebase master
   ```  

6. **Don’t commit unnecessary files** – node modules, build artifacts, logs, or temporary IDE files should be ignored (`.gitignore`).  

7. **Document important changes** – if your contribution affects setup, usage, or configuration, update the README or other documentation.  

8. **Check for sensitive information in comments or logs** – Remove any identifying personal information, passwords, internal URLs, or secret tokens.  

Following these guidelines ensures that contributions are safe, consistent, and easy to review.

## When you're ready to commit:

Stage your changes with 
```
git add .
or
git add c:/file/changed/1.txt
```

Then commit your changes with 
```bash
git commit -m "Description of changes, what you are committing"
```
Push your branch to your fork
```bash
git push origin feature/<branch-name>
```

## Before Submitting a Pull Request

Before opening a pull request, make sure:

- Tests have been added or updated where appropriate.
- Code is documented, readable, and follows the project guidelines.
- Relevant documentation has been updated if the change affects setup, usage, configuration, or behaviour.
- Linting and formatting have been run.
- No secrets, credentials, or unnecessary files are included.

Pull requests that do not meet these requirements may require changes before they can be merged.

Once you have confirmed:

Open a Pull request - https://github.com/Chameleon-company/Planting-Optimisation-Tool/compare

Fill out the PR template and click Create Pull request.


