from django.core.management import call_command
from django.test import TestCase

from terracommon.terra.models import Layer
from terracommon.terra.tests.utils import get_files_tests


class ImportShapefileTest(TestCase):
    def test_default_group_nogroup(self):
        # Sample ShapeFile
        shapefile_path = get_files_tests('shapefile-WGS84.zip')
        sample_shapefile = open(shapefile_path, 'rb')

        # Fake json schema
        empty_geojson = get_files_tests('empty.json')

        call_command(
            'import_shapefile',
            f'-iID_PG',
            f'-g{sample_shapefile.name}',
            f'-s{empty_geojson}',
            verbosity=0)

        # Retrieve the layer
        layer = Layer.objects.all()[0]
        self.assertEqual('__nogroup__', layer.group)

        # Assert the identifier is not an UUID4
        self.assertTrue(len(str(layer.features.first().identifier)) < 32)

    def test_reprojection(self):
        # Sample ShapeFile
        shapefile_path = get_files_tests('shapefile-RFG93.zip')
        sample_shapefile = open(shapefile_path, 'rb')

        # Create a fake json schema
        empty_geojson = get_files_tests('empty.json')

        call_command(
            'import_shapefile',
            f'-g{sample_shapefile.name}',
            f'-s{empty_geojson}',
            verbosity=0)

        # Retrieve the layer
        layer = Layer.objects.all()[0]
        self.assertEqual('__nogroup__', layer.group)

        # assert data was reprojected
        bbox = layer.features.first().get_bounding_box()
        self.assertTrue(-180 <= bbox[0])
        self.assertTrue(-90 <= bbox[1])
        self.assertTrue(bbox[2] <= 180)
        self.assertTrue(bbox[3] <= 90)

    def test_default_group(self):
        # Sample ShapeFile
        shapefile_path = get_files_tests('shapefile-WGS84.zip')
        sample_shapefile = open(shapefile_path, 'rb')

        # Fake json
        empty_json = get_files_tests('empty.json')
        foo_bar_json = get_files_tests('foo_bar.json')

        # Import a shapefile
        call_command(
            'import_shapefile',
            '-iID_PG',
            '-g', sample_shapefile.name,
            '-s', empty_json,
            verbosity=0)

        # Ensure old settings
        layer = Layer.objects.all()[0]
        self.assertNotEqual('new_name', layer.name)
        self.assertNotEqual('new_group', layer.group)
        self.assertNotEqual({'foo': 'bar'}, layer.schema)
        self.assertNotEqual({'foo': 'bar'}, layer.settings)

        # Change settings
        call_command(
            'layer_edit',
            '-pk', layer.pk,
            '-l', 'new_name',
            '-gr', 'new_group',
            '-s', foo_bar_json,
            '-ls', foo_bar_json
        )

        # Ensure new settings
        layer = Layer.objects.all()[0]
        self.assertEqual('new_name', layer.name)
        self.assertEqual('new_group', layer.group)
        self.assertEqual({'foo': 'bar'}, layer.schema)
        self.assertEqual({'foo': 'bar'}, layer.settings)
