from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",    # Redis as message broker
    backend="redis://localhost:6379/0",      # Redis as result backend
    include=['src.worker.tasks']  # Add this line to include tasks
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
