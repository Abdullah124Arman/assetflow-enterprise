from rest_framework import serializers
from .models import AssetCategory

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'custom_fields', 'created_at']

    def validate_custom_fields(self, value):
        # Validate that custom_fields is a list of dictionaries with required keys
        if not isinstance(value, list):
            raise serializers.ValidationError("custom_fields must be a list")
        for field in value:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Each custom_field must be a dictionary")
            required_keys = {'key', 'label', 'type', 'required'}
            if not required_keys.issubset(field.keys()):
                raise serializers.ValidationError(f"Each custom_field must contain {required_keys}")
        return value
