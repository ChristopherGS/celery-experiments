# Asynchronous Tasks with FastAPI and Celery

## Want to use this project?

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Open your browser to [http://localhost:8004](http://localhost:8004) to view the app or to [http://localhost:5556](http://localhost:5556) to view the Flower dashboard.

Open the interactive docs (`http://localhost:8004/docs`) and you'll note the `/tasks-group-async` and `/tasks-group-sync` endpoints.
These are what we will compare. Kick off one and then open up celery flower on [http://localhost:5556/](http://localhost:5556/)

On my machine 
