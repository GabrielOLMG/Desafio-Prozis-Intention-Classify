from rest_framework.test import APITestCase

from desafio_prozis.core.models import UserIntention

HTTP_200 = 200
HTTP_400 = 400


class ClassifyAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.intent = UserIntention.objects.create(
            text="product_info",
            ml_text="consultar informações do produto",
        )

    def test_valid_input(self):
        response = self.client.post(
            "/api/classify",
            {"text": "como tomar creatina"},
            format="json",
        )
        assert response.status_code == HTTP_200
        assert "intent" in response.data
        assert "confidence_score" in response.data

    def test_invalid_input(self):
        response = self.client.post("/api/classify", {"text": 123}, format="json")
        assert response.status_code == HTTP_400
        response = self.client.post(
            "/api/classify",
            {"text": {"valor extra": "erro"}},
            format="json",
        )
        assert response.status_code == HTTP_400
