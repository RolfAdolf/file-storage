# Apply migrations
flask db migrate
flask db upgrade

# Run the wsgi server
uwsgi --ini /code/config/uwsgi/uwsgi.ini
