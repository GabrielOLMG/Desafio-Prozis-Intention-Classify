from rest_framework import serializers


class ClassifyInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)

    def validate_text(self, value):
        if value.isnumeric():
            error = "O campo 'text' não pode ser apenas números."
            raise serializers.ValidationError(error)
        return value


class ClassifyOutputSerializer(serializers.Serializer):
    intent = serializers.CharField()
    confidence_score = serializers.FloatField()
