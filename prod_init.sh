# Initialize the DB without inserting dummy information

source venv/bin/activate
python manage.py recreate_db
python manage.py setup_prod
