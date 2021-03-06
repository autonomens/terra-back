from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from terracommon.accounts.tests.factories import TerraUserFactory
from terracommon.terra.models import Feature
from terracommon.terra.tests.factories import LayerFactory


class SchemaValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = TerraUserFactory()

        self.client.force_authenticate(user=self.user)

        self.layer = LayerFactory(
            name="tree",
            schema={
                "name": {
                    "type": "string"
                },
                "age": {
                    "type": "integer"
                }
            })

    def test_feature_with_valid_properties_is_posted(self):
        """Feature with valid properties is successfully POSTed"""
        response = self.client.post(
                        reverse('terra:feature-list', args=[self.layer.id, ]),
                        {
                                "geom": "POINT(0 0)",
                                "layer": self.layer.id,
                                "name": "valid tree",
                                "age": 10,
                                "properties": {},
                        },
                        format='json',)
        features = Feature.objects.all()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0].properties['name'], 'valid tree')

    def test_feature_with_missing_property_type_is_not_posted(self):
        """Feature with missing property type is not successfully POSTed"""
        response = self.client.post(
                        reverse('terra:feature-list', args=[self.layer.id, ]),
                        {
                            "geom": "POINT(0 0)",
                            "layer": self.layer.id,
                            "name": "invalid tree"
                        },
                        format='json')

        self.assertEqual(response.status_code, 400)
