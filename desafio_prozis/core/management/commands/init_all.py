# ruff: noqa: PGH004
# flake8: noqa
# isort: skip_file
# mypy: ignore-errors
# pylint: skip-file
# pyright: ignore


import json
from pathlib import Path

from constance import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from desafio_prozis.core.models import UserIntention
from desafio_prozis.ml_models.models import UnitTest
from desafio_prozis.ml_models.models import UnitTestProcess
from desafio_prozis.ml_models.workflows.label_clustering import get_or_train_model


class Command(BaseCommand):
    help = "Inicializa o banco de dados com dados padrões"

    def handle(self, *args, **kwargs):
        self.create_admin_superuser()
        self.create_unit_test_process()
        self.create_user_intention()
        self.create_unit_tests()
        self.train_model()

    def create_admin_superuser(self):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
        else:
            pass

        print("✅ Superuser admin com Senha admin criada com sucesso.")

        return True

    def create_unit_test_process(self):
        if UnitTestProcess.objects.all():
            pass
        else:
            UnitTestProcess.objects.create()

        print("✅ Processo de Teste Unitario Criado com sucesso.")

    def create_user_intention(self):
        with open("setup_files/user_intention.json", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 2. Extrair os dados do "fields" e construir objetos
        user_intentions = []
        for entry in raw_data:
            fields = entry["fields"]
            pk = entry["pk"]

            user_intentions.append(
                UserIntention(
                    id=pk,
                    text=fields["text"],
                    ml_text=fields["ml_text"],
                )
            )

        # 3. Salvar em lote (preservando os PKs)
        with transaction.atomic():
            UserIntention.objects.bulk_create(user_intentions, ignore_conflicts=True)

        print(f"✅ Importados {len(user_intentions)} UserIntentions com sucesso.")

    def create_unit_tests(self):
        # Carregue seu JSON como dicionário Python
        with open("setup_files/UnitTest-2025-05-04.json", encoding="utf-8") as f:
            data = json.load(f)

        # 2. Buscar todos os UserIntentions necessários em 1 query
        intention_ids = set(item["expected_label"] for item in data)
        intentions = {
            i.id: i for i in UserIntention.objects.filter(id__in=intention_ids)
        }

        # 3. Criar os objetos UnitTest
        unit_tests = []
        for item in data:
            try:
                intention = intentions[item["expected_label"]]
            except KeyError:
                raise ValueError(
                    f"UserIntention id={item['expected_label']} não existe."
                )

            unit_tests.append(
                UnitTest(
                    text=item["text"],
                    expected_label=intention,
                    custom_test=item["custom_test"],
                )
            )

        # 4. Salvar em lote
        with transaction.atomic():
            UnitTest.objects.bulk_create(
                unit_tests, ignore_conflicts=True, batch_size=1000
            )

        print(f"✅ Importados {len(unit_tests)} UnitTest com sucesso.")

    def train_model(self):
        model_cluster_name = config.MODEL_CLUSTERS_EMBEDING_NAME
        model_path = Path(settings.MEDIA_ROOT) / config.PATH_CLUSTERS_DATA

        get_or_train_model(
            model_name=model_cluster_name,
            model_path=model_path,
            train_again=False,
        )

        print("✅ Modelo Treinado Com Sucesso")
