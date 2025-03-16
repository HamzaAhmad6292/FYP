#!/usr/bin/env bash

# Start Auth Service
cd auth-service
source venv/bin/activate
uvicorn app.main:app --reload --port 2000 &
cd ..

# Start CRM Service
cd crm_integration_service
source .venv/bin/activate
uvicorn app.api.main:app --reload --port 5000 &
cd ..

# Start Reporting Service
cd reporting_service
source .venv/bin/activate
cd app
uvicorn main:app --reload --port 6000 &
cd ../..

# Wait for all processes to finish
wait
