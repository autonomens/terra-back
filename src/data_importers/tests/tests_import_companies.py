import csv
import tempfile

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from terra.models import Layer, Feature


class ImportCompaniesTestCase(TestCase):
    def call_command_with_tempfile(self, csv_rows, args=[], opts={}):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir='.', suffix='.csv') as tf:
            with open(tf.name, 'w') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(csv_rows)
            args += ['--source={}'.format(f.name)]
            call_command('import_companies', *args, **opts)

    def test_simple_import(self):
        company_layer = Layer.objects.get_or_create(name='company')[0]
        initial = Feature.objects.filter(layer=company_layer).count()
        self.call_command_with_tempfile(
            csv_rows=[['SIREN', 'NIC', 'L1_NORMALISEE', 'L2_NORMALISEE', 'L3_NORMALISEE'],
                      ['437582422', '00097', '52 RUE JACQUES BABINET', '31100 TOULOUSE', 'France']]
        )
        expected = initial + 1
        self.assertEqual(Feature.objects.filter(layer=company_layer).count(), expected)
        feature = Feature.objects.get(layer=company_layer, properties__SIREN='437582422', properties__NIC='00097')
        self.assertEqual(feature.properties.get('L1_NORMALISEE', ''), '52 RUE JACQUES BABINET')

    def test_init_options(self):
        company_layer = Layer.objects.get_or_create(name='company')[0]
        for i in range(2):
            Feature.objects.create(geom=Point(), properties={'SIREN': '', 'NIC': ''}, layer=company_layer)
        self.assertEqual(Feature.objects.filter(layer=company_layer).count(), 2)
        self.call_command_with_tempfile(
            csv_rows=[['SIREN', 'NIC', 'L1_NORMALISEE', 'L2_NORMALISEE', 'L3_NORMALISEE'],
                      ['437582422', '00097', '52 RUE JACQUES BABINET', '31100 TOULOUSE', 'France'],
                      ['518521414', '00038', '11 RUE DU MARCHIX', '44000 NANTES', 'France'],
                      ['518521414', '00053', '52 RUE JACQUES BABINET', '31100 TOULOUSE', 'France'],
                      ['813792686', '00012', 'BOIS DE TULLE', '32700 LECTOURE', 'France'],
                      ['822869632', '00023', '52 RUE JACQUES BABINET', '31100 TOULOUSE', 'France']],
            args=[
                '--init',
                '--creations-per-transaction=2',
                '--bulk'
            ]
        )
        self.assertEqual(Feature.objects.filter(layer=company_layer).count(), 5)
        feature = Feature.objects.get(layer=company_layer, properties__SIREN='437582422', properties__NIC='00097')
        self.assertEqual(feature.properties.get('L1_NORMALISEE', ''), '52 RUE JACQUES BABINET')

    def test_import_with_creations_and_updates(self):
        company_layer = Layer.objects.get_or_create(name='company')[0]
        Feature.objects.create(
            geom=Point(),
            properties={
                'SIREN': '437582422',
                'NIC': '00097',
                'L1_NORMALISEE': '36 RUE JACQUES BABINET',
                'L2_NORMALISEE': '31100 TOULOUSE',
                'L3_NORMALISEE': 'France',
            },
            layer=company_layer
        )
        initial = Feature.objects.filter(layer=company_layer).count()
        self.call_command_with_tempfile(
            csv_rows=[['SIREN', 'NIC', 'L1_NORMALISEE', 'L2_NORMALISEE', 'L3_NORMALISEE'],
                      ['437582422', '00097', '52 RUE JACQUES BABINET', '31100 TOULOUSE', 'France'],
                      ['518521414', '00038', '11 RUE DU MARCHIX', '44000 NANTES', 'France']]
        )
        expected = initial + 1
        self.assertEqual(Feature.objects.filter(layer=company_layer).count(), expected)
        feature = Feature.objects.get(layer=company_layer, properties__SIREN='437582422', properties__NIC='00097')
        self.assertEqual(feature.properties.get('L1_NORMALISEE', ''), '52 RUE JACQUES BABINET')
