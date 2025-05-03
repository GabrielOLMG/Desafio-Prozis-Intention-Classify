from rest_framework import serializers


class ClassifyInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)


class ClassifyOutputSerializer(serializers.Serializer):
    intent = serializers.CharField()
    confidence_score = serializers.FloatField()
