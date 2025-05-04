from celery import shared_task

from .commons import reset_process


@shared_task
def error_handler(  # noqa: PLR0913
    contex,
    error,
    uuid,
    id_,
    class_name,
    reset=True,  # noqa: FBT002
    *args,
    **kwargs,
):
    print("----------------------------------")  # noqa: T201
    print(f"error handler! ({id_})")  # noqa: T201
    print("----------------------------------")  # noqa: T201

    print(error, uuid)  # noqa: T201

    if reset:
        reset_process(class_name, id_, "ERROR")
