# Energy Dashboard API

A Django Application and scraping scripts to support energy dashboard and infrastructure campaign frontends.

Poetry, pre-commit and ruff are used to manage its dependencies and general development lifecycle,
following the standard ofother LFG projects.

### Setup

#### Python environment

##### Poetry dependencies

- [ ] Install [Poetry](https://python-poetry.org/docs/#installation)
- [ ] Install the project's dependencies: `poetry install`

At this stage you have:

- dependencies installed, managed via `pyproject.toml` and the `poetry` command
- a virtual environment available, either through:
  - `poetry run python <args...>`
  - `poetry shell`
 
##### Install `pre-commit`

You should run `poetry run pre-commit install` to set up the pre-commits for ruff checks.

##### Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for file formatting and linting.

To check for linting errors, run `ruff check` from the root of the repository. To fix any errors automatically, run `ruff check --fix`. To auto-format files, run `ruff format`.

It's recommended to set up your code editor to auto-format files and fix linting errors automatically. If you use VSCode for example, you can do this by adding the following to your settings:

```json
"[python]": {
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  },
```

### Database


Migrate and create your local database.

```sh
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```


Create a superuser.

```sh
poetry run python manage.py createsuperuser
```


Run the server

```sh
poetry run python manage.py runserver
```

### Testing

Run all tests.

```sh
poetry run python manage.py test
```
