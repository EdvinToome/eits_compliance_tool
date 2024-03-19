# Dependencies
1. nmap
2. PostgreSQL

# Install

Create venv
```
python3 -m venv venv
```
Install requirements
```
pip install -r requirements.txt
```
Run migrations
```
python3 manage.py migrate
```

# Environment

Configure database using env.example. Database used is PostgreSQL
Run
```
python manage.py collect_eits_controls
```
to retrieve E-ITS controls

# Start server
```
python manage.py runserver
```
