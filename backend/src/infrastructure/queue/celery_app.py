"""
Celery Application Configuration
Background task processing with RabbitMQ
"""
from celery import Celery

from src.config.settings import settings

# Create Celery app
celery_app = Celery(
    "moneymind",
    broker=settings.rabbitmq_url,
    backend="redis://" + settings.redis_url.split("://")[1],  # Use Redis as result backend
    include=[
        "src.infrastructure.queue.tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # Soft limit at 55 minutes
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Concurrency
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Result backend
    result_expires=86400,  # Results expire after 24 hours
    
    # Task routes
    task_routes={
        "src.infrastructure.queue.tasks.process_document_task": {"queue": "documents"},
        "src.infrastructure.queue.tasks.generate_embeddings_task": {"queue": "embeddings"},
        "src.infrastructure.queue.tasks.sync_gmail_task": {"queue": "gmail"},
        "src.infrastructure.queue.tasks.generate_report_task": {"queue": "reports"},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "sync-gmail-hourly": {
            "task": "src.infrastructure.queue.tasks.sync_gmail_task",
            "schedule": 3600.0,  # Every hour
            "args": (),
        },
        "generate-daily-reports": {
            "task": "src.infrastructure.queue.tasks.generate_report_task",
            "schedule": 86400.0,  # Every 24 hours
            "args": (),
        },
    },
)


if __name__ == "__main__":
    celery_app.start()
