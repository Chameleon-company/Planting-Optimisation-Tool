# Contributing to Planting Optimisation Tool

This document will help you set up your environment and start contributing to the project.

---

## 1. Fork and Clone the Repository

First fork the repo to create your own copy:
https://github.com/Chameleon-company/Planting-Optimisation-Tool/fork

Then clone your fork into your local development environment
```bash
git clone https://github.com/<your-username>/Planting-Optimisation-Tool.git  # Replace <your-username> with your github username.
cd Planting-Optimisation-Tool
```
Add the project repository as remote (upstream) to keep your fork up to date.
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

## 2. Before You Commit

A few important points to keep in mind to make sure your contributions are safe, clean, and easy to review:  

1. **Never commit secrets or credentials** – do not include API keys, passwords, or `.env` files in your commits. Use environment variables or secret management instead.  

2. **Run linting and formatting** – make sure your code follows the project’s style guidelines before committing:

Frontend:
```bash
npm run lint:scripts    # frontend scripts
npm run lint:styles     # frontend styles
npm run format          # frontend formatting
```

Frontend pre-commit hooks (Husky + lint-staged) automatically run validation and linting checks before commit.

Backend / Data Science / GIS:
```bash
uv run pre-commit run --all-files
```

Pre-commit hooks are configured to automatically run linting and formatting checks on staged files before commit.

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

## 3. When You're Ready to Commit:

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
Then push your changes **locally** to your fork with 
```bash
git push origin feature/<branch-name>
```
## 4. Important - Before Submitting a PR

- Your code **MUST** include new or updated test cases where applicable, and all existing tests must continue to pass before submitting a PR.
- Your Code **SHOULD** follow the repository formatting, linting, and contribution guidelines documented in this repository.
- Your code **MUST** be linked to an assigned GitHub issue, user story, or task before submitting a PR.

Failure to adhere to any of the above will result in your PR **not being accepted**.

Once you have confirmed:

Open a Pull request - https://github.com/Chameleon-company/Planting-Optimisation-Tool/compare

Fill out the PR template and click Create Pull request.

## 5. Setup Guides

- [Frontend](https://github.com/Chameleon-company/Planting-Optimisation-Tool/tree/master/frontend#how-to-run-the-frontend)
- [Backend](https://github.com/Chameleon-company/Planting-Optimisation-Tool/tree/master/backend#getting-started)
- [Data Science](https://github.com/Chameleon-company/Planting-Optimisation-Tool/blob/master/datascience/README.md)
- [GIS](https://github.com/Chameleon-company/Planting-Optimisation-Tool/blob/master/gis/README.md)
