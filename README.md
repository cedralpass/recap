# recap

#setup
## Init DB
Run the following command to init DB
```bash
flask --app recap init-db   
```

## Init dev webserver
Run the following command to run the development, builtin webserver

### For just the recap service: 
```bash
flask --app recap run --debug  --port 8081
```
[recap index page](http://127.0.0.1:8081/)

### For just the aiapi service: 
```bash
flask --app aiapi run --debug  --port 8082
```

### Two run recap and aiapi together with
/ -> recap
/aiapi -> aiapi

use the following script
```bash
python run.py
```

[recap index page ](http://127.0.0.1:8001/)
[aiapi hello function ](http://127.0.0.1:8001/aiapi/hello)

# Produciton
## recap - Run the produciton gunicorn web server
Run the following command to run in produciton
```bash
gunicorn -w 4 'recap:create_app()' -b 127.0.0.1:8080 --access-logfile=gunicorn.http.log --error-logfile=gunicorn.error.log
```

## aiapi - Run the produciton gunicorn web server
Run the following command to run the aiapi produciton
```bash
gunicorn -w 4 'aiapi:create_app()' -b 127.0.0.1:8080 --access-logfile=gunicorn.http.log --error-logfile=gunicorn.error.log
```

## recap + aiapi - Run recap and aiapi together under one server

```bash
 gunicorn -w 4 'app' -b 127.0.0.1:8080 --access-logfile=gunicorn.http.log --error-logfile=gunicorn.error.log
```

[recap index page ](http://127.0.0.1:8080/)
[aiapi hello function ](http://127.0.0.1:8080/aiapi/hello)

[gunicorn settings](https://docs.gunicorn.org/en/stable/settings.html)
