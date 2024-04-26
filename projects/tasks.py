from celery import shared_task

from projects.models import Projects
from projects.utils import generate_doc

@shared_task()
def celery_generate_doc(project_id: int ):
    project = Projects.objects.get(id=project_id)
    generate_doc(project)



