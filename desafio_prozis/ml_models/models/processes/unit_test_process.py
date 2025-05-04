from desafio_prozis.ml_models.models.processes.celery_common import CeleryCommon
from desafio_prozis.ml_models.tasks.global_tasks.error_handler import error_handler
from desafio_prozis.ml_models.tasks.global_tasks.success_handler import success_handler
from desafio_prozis.ml_models.tasks.unit_test_tasks import unit_test


class UnitTestProcess(CeleryCommon):
    def __str__(self):
        return f"Teste Unitario :{self.id}"

    def process_unit_test(self, **kwargs):
        id_process = self.id

        unit_test.apply_async(
            (id_process,),
            link=success_handler.s(id_=id_process, class_name="UnitTestProcess"),
            link_error=error_handler.s(id_=id_process, class_name="UnitTestProcess"),
        )
