from celery import shared_task

from .commons import reset_process


@shared_task
def success_handler(
    process_id,
    id_,
    class_name,
    reset=True,  # noqa: FBT002
    *args,
    **kwargs,
):
    print("----------------------------------")  # noqa: T201
    print(f"Success handler! (uuid, {id_})")  # noqa: T201
    print("----------------------------------")  # noqa: T201

    if reset:
        reset_process(class_name, id_, "SUCCESS")
