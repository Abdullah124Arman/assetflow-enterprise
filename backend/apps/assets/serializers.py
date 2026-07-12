from rest_framework import serializers
from .models import AssetCategory, Asset

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

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id', 'tag', 'name', 'category_id', 'serial_number', 'qr_code', 
            'acquisition_date', 'acquisition_cost', 'condition', 'location', 
            'status', 'is_bookable', 'department_id', 'custom_field_values', 
            'photo_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tag', 'status', 'created_at', 'updated_at']

    def validate_custom_field_values(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("custom_field_values must be an object (dictionary)")
        return value


class AssetHistorySerializer(serializers.Serializer):
    # This is a custom serializer to merge allocations and maintenance requests
    id = serializers.UUIDField()
    type = serializers.CharField()
    date = serializers.DateTimeField()
    status = serializers.CharField()
    details = serializers.DictField()
