# Contributing to Planting Optimisation Tool

This document will help you set up your environment and start contributing to the project.

---

## 1. Fork and Clone the repository

First fork the repo to create your own copy:
https://github.com/Chameleon-company/Planting-Optimisation-Tool/fork

Then clone your fork locally
```bash
git clone https://github.com/<your-username>/Planting-Optimisation-Tool.git
cd Planting-Optimisation-Tool
```
Add the project repo as remote to keep your fork up to date
```bash
git remote add upstream https://github.com/Chameleon-company/Planting-Optimisation-Tool.git
git remote -v
```

## 2. Front-end setup

The front-end is built with React. Make sure you have **Node.js (v18+)** and **npm** installed.
https://nodejs.org/en/download
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

then
```bash
cd frontend
npm install
```
then to start the development server
```bash
npm start
```



## 3. Back-end and Datascience setup

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

To run, from the base directory of your team, enter `ruff check` and it will test your code for issues. You can also choose to run `ruff check --fix` to automatically fix any linting issues.

##TODO: Have it run on PR automatically with github CI

