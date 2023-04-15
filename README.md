# Flake8 Maximo
A Flake8 plugin which checks a file for maximo specific linting rules:
 - MAX100 Check that mboSet.count() is not called more than once per mboSet
 - MAX101 Check that mboSet.count() is not called within loops
 - MAX102 Check that MboConstants are used in stead of literals

## Installation
```bash
pip install git+https://github.com/SnowcolaLabs/flake8-maximo.git
```

## Development
```bash
pip install -r ./requirements/dev.txt

# install the plugin in editable mode
pip instell -e .
```

## Testing
run pytest
```bash
pytest tests
```
