import unittest
from typing import Dict, Any
from nougat import nougat, init_nougat, init_nougat_global, nougat_patch


class TestNougat(unittest.TestCase):

    def setUp(self):
        """Prepare test data before each test."""
        self.data: Dict[str, Any] = {
            'controller': {
                'flags': {
                    'create_workflow_connections': True,
                    'delete_on_fail': False
                },
                'settings': {
                    'timeout': 30
                }
            },
            'user': {
                'name': 'Alice',
                'permissions': ['read', 'write']
            }
        }

    # ✅ Test init_nougat on individual dictionaries
    def test_init_nougat(self):
        """Test if nougat is correctly added to dictionary instances."""
        init_nougat(self.data)
        self.assertTrue(hasattr(self.data, 'nougat'))
        self.assertTrue(self.data.nougat('controller', 'flags', 'create_workflow_connections'))

    # ✅ Test nested dictionary retrieval
    def test_nougat_nested(self):
        """Test nougat method with deeply nested dictionaries."""
        init_nougat(self.data)
        self.assertEqual(self.data.nougat('controller', 'flags', 'create_workflow_connections'), True)
        self.assertEqual(self.data.nougat('controller', 'settings', 'timeout'), 30)
        self.assertEqual(self.data.nougat('user', 'name'), 'Alice')

    # ✅ Test missing keys with default values
    def test_nougat_missing_keys(self):
        """Test retrieval with missing keys and default values."""
        init_nougat(self.data)
        self.assertEqual(self.data.nougat('controller', 'flags', 'missing_key', default='default_value'), 'default_value')
        self.assertIsNone(self.data.nougat('controller', 'flags', 'nonexistent'))

    # ✅ Test monkey-patch with global initialization
    def test_init_nougat_global(self):
        """Test the global patching of all dictionaries."""
        init_nougat_global()

        # New dictionary should have nougat method globally
        new_data = {'key': {'nested': 'value'}}
        self.assertTrue(hasattr(new_data, 'nougat'))
        self.assertEqual(new_data.nougat('key', 'nested'), 'value')
        self.assertEqual(new_data.nougat('missing', default='not found'), 'not found')

    # ✅ Test dictionary monkey-patching with `nougat_patch`
    def test_nougat_patch(self):
        """Test dictionary patching globally with dynamic `nougat` addition."""
        nougat_patch()

        dict1 = {'a': {'b': {'c': 123}}}
        dict2 = {'x': {'y': {'z': 456}}}

        # Verify nougat dynamically attaches to all dicts
        self.assertEqual(dict1.nougat('a', 'b', 'c'), 123)
        self.assertEqual(dict2.nougat('x', 'y', 'z'), 456)
        self.assertEqual(dict1.nougat('a', 'b', 'missing', default='default'), 'default')

    # ✅ Test handling of non-dict-like objects
    def test_invalid_object(self):
        """Test init_nougat with an invalid object."""
        with self.assertRaises(AttributeError):
            init_nougat(['not', 'a', 'dict'])

        with self.assertRaises(AttributeError):
            init_nougat('string instead of dict')

    # ✅ Test mixed types in nested keys
    def test_mixed_types(self):
        """Test mixed types in nested keys."""
        complex_data = {
            'a': [
                {'b': 'value1'},
                {'c': 'value2'}
            ],
            'x': 'final'
        }
        init_nougat(complex_data)

        # Ensure proper retrieval even with list nesting
        self.assertEqual(complex_data.nougat('a', 0, 'b'), 'value1')
        self.assertEqual(complex_data.nougat('x'), 'final')
        self.assertEqual(complex_data.nougat('a', 1, 'c'), 'value2')
        self.assertIsNone(complex_data.nougat('a', 2, 'missing'))

    # ✅ Test nougat on empty dictionary
    def test_nougat_empty_dict(self):
        """Test nougat on an empty dictionary."""
        empty_dict = {}
        init_nougat(empty_dict)
        self.assertIsNone(empty_dict.nougat('missing', default=None))
        self.assertEqual(empty_dict.nougat('missing', default='fallback'), 'fallback')

    # ✅ Test performance with large nested dict
    def test_nougat_large_dict(self):
        """Test nougat on a large dictionary."""
        large_dict = {'key' + str(i): {'nested' + str(i): i} for i in range(1000)}
        init_nougat(large_dict)

        # Check boundary keys
        self.assertEqual(large_dict.nougat('key999', 'nested999'), 999)
        self.assertEqual(large_dict.nougat('key500', 'nested500'), 500)
        self.assertIsNone(large_dict.nougat('key1001', 'nested1001'))


if __name__ == '__main__':
    unittest.main()
