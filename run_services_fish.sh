#!/usr/bin/env fish

# Start Auth Service
cd auth-service
fish -c "source venv/bin/activate.fish; uvicorn app.main:app --reload --port 2000" &
cd ..

# Start CRM Service
cd crm_integration_service
fish -c "source .venv/bin/activate.fish; uvicorn app.api.main:app --reload --port 5000 & celery -A app.worker.celery_app worker --loglevel=info -P gevent --concurrency=1" &
cd ..

# Start Reporting Service
cd reporting_service
fish -c "source .venv/bin/activate.fish; cd app; uvicorn main:app --reload --port 6000" &
cd ..

# Wait for all processes to finish
wait
