# Répondeur

## Requirements

Python 3.6+

## Setup

```
$ pipenv install
$ pipenv shell
```

## Initialize the database

```
$ zam_init_db development.ini
```

## Start the web app

```
$ pserve development.ini --reload
```

You can now access the web app at http://localhost:6543/

## Development

Run tests:

```
$ pytest
```

Reformat code:

```
$ black .
```

Check style guide:

```
$ flake8
```

Check type annotations:

```
mypy zam_repondeur
```
