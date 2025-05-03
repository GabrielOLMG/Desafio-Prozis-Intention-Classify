from transformers import Pipeline
from transformers import pipeline


def get_zero_shot_model(
    model_text: str,
    hypothesis_template: str,
) -> Pipeline:
    return pipeline(
        "zero-shot-classification",
        model=model_text,
        hypothesis_template=hypothesis_template,
    )


def get_text_label(
    classifier: Pipeline,
    text: str,
    labels: list,
    *,
    get_best: bool = False,
) -> list:
    resultado = classifier(text, candidate_labels=labels)
    if not get_best:
        return list(zip(resultado["labels"], resultado["scores"], strict=False))
    return list(zip(resultado["labels"], resultado["scores"], strict=False))
