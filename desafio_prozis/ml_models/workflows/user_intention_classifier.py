import logging
from pathlib import Path

from constance import config
from django.conf import settings

from desafio_prozis.core.models import UserIntention
from desafio_prozis.ml_models.workflows.label_clustering import get_cluster_labels
from desafio_prozis.ml_models.workflows.label_clustering import get_or_train_model
from desafio_prozis.ml_models.workflows.zero_shot_classifier import get_text_label
from desafio_prozis.ml_models.workflows.zero_shot_classifier import get_zero_shot_model

logger = logging.getLogger(__name__)


def classify_user_intention(text: str) -> tuple[str, float]:
    logger.info("Iniciando Processo de Captura de Intenção")

    model_zero_shot_name = config.ZERO_SHOT_MODEL_NAME
    model_cluster_name = config.MODEL_CLUSTERS_EMBEDING_NAME
    hypothesis_template = config.ZERO_SHOT_MODEL_HYPOTHESIS

    model_path = Path(settings.MEDIA_ROOT) / config.PATH_CLUSTERS_DATA

    # Resgata Modelo de Cluster para Labels
    logger.info("Carregando Modelo de Cluster")
    model_data, created = get_or_train_model(
        model_name=model_cluster_name,
        model_path=model_path,
        train_again=False,
    )
    logger.info("Modelo de Cluster Carregado")

    logger.info("Aplicando Modelo de Cluster")
    labels_filtered = get_cluster_labels(text, model_data, n_best=3)
    labels_filtered = [str(label) for label, score in labels_filtered]
    logger.info("Possíveis Labels: %s", labels_filtered)

    logger.info("Carregando Modelo Zero Shot")
    zero_shot_model = get_zero_shot_model(model_zero_shot_name, hypothesis_template)

    logger.info("Calculando Intenção do Usuario")
    label, score = get_text_label(zero_shot_model, text, labels_filtered, get_best=True)
    label = UserIntention.objects.get(ml_text=label).text

    logger.info("[RESULTADO] Texto '%s' Label %s Score %s ", text, label, score)

    return label, score
