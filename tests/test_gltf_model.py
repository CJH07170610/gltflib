import json
from unittest import TestCase
from gltflib import GLTFModel, Asset, Buffer


class TestGLTFModel(TestCase):
    def test_init(self):
        """
        Basic test ensuring the successful initialization of a GLTF2 model when all required properties are passed
        in. Note the only required property in a GLTF2 model is the asset.
        """
        # Act
        model = GLTFModel(asset=Asset())

        # Assert
        self.assertIsInstance(model, GLTFModel)

    def test_init_missing_property(self):
        """Ensures model initialization results in error if a required property is missing"""
        # Act/Assert
        with self.assertRaisesRegex(TypeError, 'asset'):
            _ = GLTFModel()

    def test_asset_version_default(self):
        """Ensures asset version is initialized as 2.0 if not passed in"""
        # Act
        model = GLTFModel(asset=Asset())

        # Assert
        self.assertEqual(model.asset.version, '2.0')

    def test_asset_version(self):
        """Ensures asset version is retained if a value is passed in"""
        # Act
        model = GLTFModel(asset=Asset(version='2.1'))

        # Assert
        self.assertEqual(model.asset.version, '2.1')

    def test_to_json_removes_empty_properties(self):
        """
        Ensures that any properties in the model that are "empty" (empty strings, lists, etc.) are deleted when
        encoding the model to JSON.
        """
        # Arrange
        model = GLTFModel(asset=Asset(generator='', minVersion=None), buffers=[])

        # Act
        v = model.to_json()

        # Assert
        data = json.loads(v)
        self.assertDictEqual(data, {'asset': {'version': '2.0'}})

    def test_decode(self):
        """Ensures that a simple model can be decoded successfully from JSON."""
        # Arrange
        v = '{"asset": {"version": "2.1"}, "buffers": [{ "uri": "triangle.bin", "byteLength": 44 }]}'

        # Act
        model = GLTFModel.from_json(v)

        # Assert
        self.assertEqual(model, GLTFModel(asset=Asset(version='2.1'), buffers=[Buffer(uri='triangle.bin', byteLength=44)]))

    def test_decode_missing_required_property(self):
        """
        Ensures that an error is raised when decoding a model from JSON if any required properties are missing.
        In this case, the version property on the asset is missing.
        """
        # Arrange
        v = '{}'

        # Act/Assert
        with self.assertRaisesRegex(TypeError, 'version.*Asset'):
            _ = GLTFModel.from_json(v)
