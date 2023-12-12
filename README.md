# fastapi-md5-demo
A demo application that calculates the MD5 hash of a provided file. Use of the following stack is demonstrated:
- fastapi
- sqlalchemy
- postgres
- celery
- rabbitmq
- docker / docker-compose


### Requirements
- docker, docker-compose
- this project was developed and tested on Linux, though it should work on other operating systems


### Running Project
Instructions to launch the project

1. Copy over `default.env` to `.env`. There should be no need to adjust them.
```sh
cat default.env > .env
```

2. Launch project with `docker-compose`
```sh
docker-compose up --build
```

Note: sometimes the app will fail to start the first time because of the initial database migrations. Just CTRL-C to cancel and try again.

3. Navigate to your browser to http://localhost:8000 for access to the webapp. Further instructions are provided there.


### Optional API Usage
The webapp functionality is also accessible via API

1. Upload a file

```sh
➜ curl -s -F file=@example.txt http://localhost:8000/api/file | jq
{
  "req_id": "f62e0437-883f-4562-a551-dd0da38d2e10",
  "file_name": "example.txt",
  "md5_hash": null,
  "processed": false,
  "received_at": "2023-12-12T09:06:55.804321",
  "processed_at": null
}
```

2. Retrieve the file's MD5 hash, by querying the API using the received `req_id`

```sh
➜ curl -s http://localhost:8000/api/hash/f62e0437-883f-4562-a551-dd0da38d2e10 | jq

{
  "req_id": "f62e0437-883f-4562-a551-dd0da38d2e10",
  "file_name": "example.txt",
  "md5_hash": "9108f5825a0f3af01e914265c924d9c5",
  "processed": true,
  "received_at": "2023-12-12T09:06:55.804321",
  "processed_at": "2023-12-12T09:06:55.823961"
}
```


### Log File
Workers output additional logs to `/logs/app.log` using JSONL. Example entry:

```json
{
    "text": "{\"timestamp\": \"2023-12-11T10:18:49.221487+00:00\", \"worker\": \"worker1\", \"file_hash\": \"76f091f11e01e083262873f28ae44ab7\"}\n",
    "record": {
        "elapsed": {"repr": "0:00:30.550093", "seconds": 30.550093},
        "exception": null,
        "extra": {"worker": "worker1", "file_hash": "76f091f11e01e083262873f28ae44ab7", "serialized": "{\"timestamp\": \"2023-12-11T10:18:49.221487+00:00\", \"worker\": \"worker1\", \"file_hash\": \"76f091f11e01e083262873f28ae44ab7\"}"},
        "file": {"name": "worker.py", "path": "/worker/src/app/worker.py"},
        "function": "hash_file",
        "level": {"icon": "ℹ️", "name": "INFO", "no": 20},
        "line": 38, "message": "logging file hash", "module": "worker", "name": "app.worker",
        "process": {"id": 10, "name": "ForkPoolWorker-1"},
        "thread": {"id": 139943061665600, "name": "MainThread"},
        "time": {"repr": "2023-12-11 10:18:49.221487+00:00",
        "timestamp": 1702289929.221487}
    }
}
```

The `text` field contains relevant fields that can be set in the [logger file](./src/app/logger.py). (The `record` fields are default loguru fields and can be ignored.)

Any arbitrary amount of workers can append to the log file. Loguru ensures log message integrity by being thread/multiprocess-safe via it's built-in log message buffering/queueing