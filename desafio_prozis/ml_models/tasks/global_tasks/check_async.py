from django.utils import timezone

from .commons import get_model


def check_async(task, process_id, class_name, action, change):
    class_object = get_model(class_name)
    model = class_object.objects.get(id=process_id)

    if task.request.id:
        print("Running async!")  # noqa: T201
        if change:
            model.celery_task = task.request.id
            model.celery_running = True
            model.celery_status = "ON GOING"
            model.current_action = action
            model.started = timezone.now()
            model.save()
    else:
        print("Not running async!")  # noqa: T201

    return model
