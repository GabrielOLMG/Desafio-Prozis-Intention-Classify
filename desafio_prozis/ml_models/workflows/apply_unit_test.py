from desafio_prozis.core.models import UserIntention
from desafio_prozis.ml_models.models import UnitTest
from desafio_prozis.ml_models.workflows.user_intention_classifier import (
    classify_user_intention,
)


def apply_unit_test() -> bool:
    unit_tests = UnitTest.objects.filter(custom_test=False)
    for unit_test in unit_tests:
        label, score = classify_user_intention(unit_test.text)
        user_intention = UserIntention.objects.get(text=label)
        unit_test.predicted_label = user_intention
        unit_test.save()

    return True
