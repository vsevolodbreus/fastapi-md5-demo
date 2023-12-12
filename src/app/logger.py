import json

from loguru import logger

from app.config import settings


def serialize(record):
    output = {}

    if "time" in record:
        output["timestamp"] = record["time"].isoformat()

    output["worker"] = record.get("extra", {}).get("worker")
    output["md5_hash"] = record.get("extra", {}).get("md5_hash")
    output["file_name"] = record.get("extra", {}).get("file_name")
    output["req_id"] = record.get("extra", {}).get("req_id")

    return json.dumps(output)


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger.remove(0)

logger = logger.patch(patching)

logger.add(
    settings.LOG_FILE, format="{extra[serialized]}", enqueue=True, serialize=True
)
