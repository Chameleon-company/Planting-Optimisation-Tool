# Contributing to Planting Optimisation Tool

This document will help you set up your environment and start contributing to the project.

---

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
   ruff check .       # backend / Data Science
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

## When you're ready to commit:

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
Open a Pull request - https://github.com/Chameleon-company/Planting-Optimisation-Tool/compare

Fill out the PR template and click Create Pull request. Then mark off your task on the MS Teams planner [here](https://teams.microsoft.com/l/entity/com.microsoft.teamspace.tab.planner/_djb2_msteams_prefix_4285208193?context=%7B%22channelId%22%3A%2219%3A040b4a55d7084ae0b2426a200c20ac53%40thread.tacv2%22%7D&tenantId=d02378ec-1688-46d5-8540-1c28b5f470f6).

# Setups

## 1. Front-end setup

The front-end is built with React. Make sure you have **Node.js (v18+)** https://nodejs.org/en/download and **npm** https://docs.npmjs.com/downloading-and-installing-node-js-and-npm installed.


Confirm installation with:
```bash
node -v # should return >18.0
npm -v
```

then
```bash
cd frontend
npm install
```
then to start the development server
```bash
npm start
```

If you get errors or white screen after pulling new changes, run `npm install` again to update dependencies.

### Testing

The front end uses eslint for linting - https://eslint.org/docs/latest/use/getting-started

Prettier for code formatting - https://prettier.io/docs/

CRA's built-in test runner for testing - https://create-react-app.dev/docs/running-tests/ **(TBC)**

They are setup so you can run:
```bash
npm lint            # for linting
npm format      # for formatting
npm test            # for testing
```


## 2. Back-end and Data Science setup

Install `uv` for your chosen OS from:
```
https://docs.astral.sh/uv/getting-started/installation/
```
and confirm it is installed with `uv --version`.
You should see something like 
```console
C:\...\Planting-Optimisation-Tool > uv --version
> uv 0.8.14
```
Then 
```bash
cd backend
```
Run `uv sync` to install all requirements from `pyproject.toml` for the backend.
```bash
cd ..
cd datascience
```
Run `uv sync` to install all requirements from `pyproject.toml` for the datascience directory.

If there are additional python packages you require, run `uv add packagename` to add it to the project.

This project uses Ruff linter and formatter (https://docs.astral.sh/ruff/tutorial/) to enforce PEP 8 style guide for python (https://peps.python.org/pep-0008/)

To run, from the base directory of your team, enter `ruff check` and it will test your code for issues. 

You can also choose to run `ruff check --fix` to automatically fix any linting issues.
