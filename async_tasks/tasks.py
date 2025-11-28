from celery import shared_task

@shared_task
def sample_task(data):
    print(f"Processing {data}")
    return True
