# Flake8 Maximo
A Flake8 plugin which checks a file for maximo specific linting rules:
 - MAX100 Check that mboSet.count() is not called more than once per mboSet
 - MAX101 Check that mboSet.count() is not called within loops

## Installation
```bash
git clone https://github.com/SnowcolaLabs/flake8-maximo.git /path/to/save

cd /path/to/save

# if using a virtualenv activate first
pip install -r ./requirments/prod.txt .
```

## Testing
Ensure dev dependencies are installed
```bash
pip install -r ./requirements/dev.txt
```
run pytest
```bash
pytest tests
```
