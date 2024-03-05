# recap

#setup
## Init DB
Run the following command to init DB
```bash
flask --app recap init-db   
```

## Init dev webserver
Run the following command to run the development, builtin webserver
```bash
flask --app recap run --debug  
```

# Produciton
## Run the produciton gunicorn web server
Run the following command to run in produciton
```bash
gunicorn -w 4 'recap:create_app()' -b 127.0.0.1:8080 --access-logfile=gunicorn.http.log --error-logfile=gunicorn.error.log
```
[gunicorn settings](https://docs.gunicorn.org/en/stable/settings.html)
