# Railway Deployment Files

## Procfile
Create a file named `Procfile` (no extension) in your project root:

```
web: gunicorn Project.wsgi --log-file -
```

## runtime.txt (Optional)
Specify Python version in `runtime.txt`:

```
python-3.11.0
```

## Install Gunicorn
```bash
pip install gunicorn
pip freeze > requirements.txt
```
