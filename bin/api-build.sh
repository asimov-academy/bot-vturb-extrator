#!/bin/sh

/home/samuel/.local/bin/poetry run uvicorn vturb.api:app --host 0.0.0.0 --port 8882