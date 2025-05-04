from django.utils import timezone


def get_model(model_name: str):
    from desafio_prozis.ml_models.models import UnitTestProcess

    model_map = {
        "UnitTestProcess": UnitTestProcess,
    }
    return model_map[model_name]


def reset_process(class_name, process_id, status):
    class_object = get_model(class_name)

    model = class_object.objects.get(id=process_id)

    model.celery_status = status
    model.last_action = f"{model.current_action} - {status}"
    model.current_action = ""
    model.celery_running = False
    model.celery_task = ""
    model.finished = timezone.now()
    model.save()
