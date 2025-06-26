#!/bin/bash --login

conda activate myenv
exec uvicorn main:app --host 0.0.0.0 --port 9696