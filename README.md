# Energy Dashboard API

A Django Application and scraping scripts to support energy dashboard and infrastructure campaign frontends.

Poetry, pre-commit and ruff are used to manage its dependencies and general development lifecycle,
following the standard of other LFG projects.

### Setup

#### Python environment

##### Poetry dependencies

- [ ] Install [Poetry](https://python-poetry.org/docs/#installation)
- [ ] Select Environment: `poetry env use <python path or alias>`
- [ ] Install the project's dependencies: `poetry install`

At this stage you have:

- dependencies installed, managed via `pyproject.toml` and the `poetry` command
- a virtual environment available, either through:
  - `poetry run python <args...>`
  - `poetry env activate` (`poetry shell` for poetry<=2.0.0)
You may need to run `& <path to venv from above command>` to activate the virtual environment in PowerShell.
 
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

Set APP_DEVELOPMENT environment variables.

```sh
export APP_DEVELOPMENT=True
$env:APP_DEVELOPMENT = "True"
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


### Project Layout

```plaintext
energy-dashboard-api/
├── api/                          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py                   # For async tasks (TODO)
├── apps/
│   ├── core/                       # Shared utilities
│   │   ├── utils/
│   │   │   ├── data_cleaners.py
│   │   │   └── api_clients.py
│   │   ├── management/
│   │   │   └── commands/          # Custom Django commands
│   │   │       ├── fetch_national_grid_data.py
│   │   │       ├── fetch_elexon_data.py
│   │   │       └── scrape_ofgem.py
│   ├── national_grid_eso/         # App for National Grid data
│   │   ├── models.py
│   │   ├── tasks.py               # Celery task for API (TODO)
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_api_client.py
│   ├── elexon/                    # Elexon market data app
│   ├── carbon_intensity/          # Carbon API app
│   └── weather/                   # Weather data app
├── static/                         # CSS/JS for future frontend
├── data/                           # Raw CSV/JSON backups and saved pages (TODO)
└── requirements.txt
```
