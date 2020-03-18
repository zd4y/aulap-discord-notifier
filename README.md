# Aulaplaneta discord notifier

This is a discord bot made using python and discord.py to receive notifications for new homeworks in [aulaplaneta](https://www.aulaplaneta.com)

I created this bot because aulaplaneta doesn't have a homework notification system and I am too lazy to keep opening the website to check for new homeworks.

## Setup/Usage

### Requirements

- Python version 3.5.3 or higher
- Pip

Install the pip requirements with `pip install -r requirements.txt`

### Required environment variables

You need an account at aulaplaneta to get access to their API.

Add the environment variables with `export` from your terminal (If you are on Windows, use `set` instead):

```
export AULAP_USERNAME={Your username}
export AULAP_PASSWORD={Your password}
export DATABASE_URL={Your database's URL}
```

### Creating the databases

Run the python interpreter in the same folder where `db.py` is located and enter the following:

```python
>>> import db
>>> db.create_all()
```

---

Then run:

`python -m bot`
