from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from desafio_prozis.ml_models.tasks.global_tasks.check_async import check_async


@shared_task(
    bind=True,
    autoretry_for=(ObjectDoesNotExist,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,
    soft_time_limit=60**6,
)
def unit_test(task, process_id):
    from desafio_prozis.ml_models.workflows.apply_unit_test import apply_unit_test

    check_async(
        task,
        process_id,
        class_name="UnitTestProcess",
        action="aplicando teste unitario",
        change=True,
    )

    apply_unit_test()
