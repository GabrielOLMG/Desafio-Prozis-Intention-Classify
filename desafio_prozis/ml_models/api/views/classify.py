from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from desafio_prozis.ml_models.api.serializers.classify import ClassifyInputSerializer
from desafio_prozis.ml_models.api.serializers.classify import ClassifyOutputSerializer
from desafio_prozis.ml_models.workflows.user_intention_classifier import (
    classify_user_intention,
)


class ClassifyUserIntentionView(APIView):
    def post(self, request):
        serializer = ClassifyInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data["text"]
        label, score = classify_user_intention(text)

        output = ClassifyOutputSerializer(
            {
                "intent": label,
                "confidence_score": round(score, 4),
            },
        )
        return Response(output.data)
