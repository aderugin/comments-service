from comments.celery import app
from django.apps import apps


@app.task
def process_comments_to_file_task(task_id):
    CommentsAsFileTask = apps.get_model('base', 'CommentsAsFileTask')
    CommentsAsFileTask.objects.get(id=task_id).prepare_file()
