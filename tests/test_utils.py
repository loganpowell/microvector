"""
Test suite for microvector utility functions.
"""

from microvector.utils import stringify_nonstring_target_values


class TestStringifyNonstringTargetValues:
    """Tests for stringify_nonstring_target_values function."""

    def test_stringify_int_values(self):
        """Test converting integer values to strings."""
        collection = [
            {"header": "First", "value": 1},
            {"header": "Second", "value": 2},
        ]

        result = stringify_nonstring_target_values(collection, "value")

        assert result[0]["value"] == "1"  # type: ignore
        assert result[1]["value"] == "2"  # type: ignore
        assert isinstance(result[0]["value"], str)  # type: ignore

    def test_stringify_bool_values(self):
        """Test converting boolean values to strings."""
        collection = [
            {"name": "Active", "is_active": True},
            {"name": "Inactive", "is_active": False},
        ]

        result = stringify_nonstring_target_values(collection, "is_active")

        assert result[0]["is_active"] == "True"  # type: ignore
        assert result[1]["is_active"] == "False"  # type: ignore

    def test_stringify_float_values(self):
        """Test converting float values to strings."""
        collection = [
            {"item": "A", "price": 99.99},
            {"item": "B", "price": 149.50},
        ]

        result = stringify_nonstring_target_values(collection, "price")

        assert result[0]["price"] == "99.99"  # type: ignore
        assert result[1]["price"] == "149.5"  # type: ignore

    def test_stringify_nested_dict(self):
        """Test converting nested dictionary values."""
        collection = [
            {"header": "Test", "nested": {"value": 123}},
        ]

        result = stringify_nonstring_target_values(collection, "value")

        assert result[0]["nested"]["value"] == "123"  # type: ignore

    def test_stringify_preserves_strings(self):
        """Test that existing strings are preserved."""
        collection = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "age": "30"},
        ]

        result = stringify_nonstring_target_values(collection, "age")

        assert result[0]["age"] == "25"  # type: ignore
        assert result[1]["age"] == "30"  # type: ignore

    def test_stringify_multiple_levels_deep(self):
        """Test converting deeply nested values."""
        collection = [{"level1": {"level2": {"level3": {"target": 999}}}}]

        result = stringify_nonstring_target_values(collection, "target")

        assert result[0]["level1"]["level2"]["level3"]["target"] == "999"  # type: ignore

    def test_stringify_ignores_non_target_keys(self):
        """Test that non-target keys are left unchanged."""
        collection = [
            {"name": "Test", "count": 5, "active": True},
        ]

        result = stringify_nonstring_target_values(collection, "count")

        assert result[0]["count"] == "5"  # type: ignore
        assert result[0]["active"] is True  # type: ignore
        assert result[0]["name"] == "Test"  # type: ignore

    def test_stringify_handles_missing_key(self):
        """Test that missing keys don't cause errors."""
        collection = [
            {"name": "Has key", "value": 1},
            {"name": "Missing key"},
        ]

        result = stringify_nonstring_target_values(collection, "value")

        assert result[0]["value"] == "1"  # type: ignore
        assert "value" not in result[1]  # type: ignore

    def test_stringify_empty_collection(self):
        """Test with empty collection."""
        collection = []  # type: ignore

        result = stringify_nonstring_target_values(collection, "value")  # type: ignore

        assert result == []

    def test_stringify_single_dict(self):
        """Test with single dictionary (not in a list)."""
        data = {"name": "Test", "count": 42}

        result = stringify_nonstring_target_values(data, "count")

        assert result["count"] == "42"  # type: ignore

    def test_stringify_primitive_types(self):
        """Test that primitive types are returned as-is."""
        assert stringify_nonstring_target_values("string", "key") == "string"
        assert stringify_nonstring_target_values(123, "key") == 123
        assert stringify_nonstring_target_values(45.67, "key") == 45.67
        assert stringify_nonstring_target_values(True, "key") is True

    def test_stringify_mixed_types_in_list(self):
        """Test with mixed types in collection."""
        collection = [
            {"item": "A", "quantity": 10},
            {"item": "B", "quantity": 20.5},
            {"item": "C", "quantity": False},
        ]

        result = stringify_nonstring_target_values(collection, "quantity")

        assert result[0]["quantity"] == "10"  # type: ignore
        assert result[1]["quantity"] == "20.5"  # type: ignore
        assert result[2]["quantity"] == "False"  # type: ignore

    def test_stringify_preserves_other_nested_structures(self):
        """Test that other nested structures are preserved."""
        collection = [
            {
                "data": {
                    "values": [1, 2, 3],
                    "target": 100,
                    "metadata": {"source": "test"},
                }
            }
        ]

        result = stringify_nonstring_target_values(collection, "target")

        assert result[0]["data"]["target"] == "100"  # type: ignore
        assert result[0]["data"]["values"] == [1, 2, 3]  # type: ignore
        assert result[0]["data"]["metadata"]["source"] == "test"  # type: ignore
