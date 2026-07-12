from rest_framework import serializers
from .models import Booking
from apps.assets.models import Asset

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'resource_asset_id', 'booked_by', 'start_time',
            'end_time', 'status', 'purpose', 'reminder_sent', 'created_at'
        ]

class BookingRequestSerializer(serializers.Serializer):
    resource_asset_id = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    purpose = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({"end_time": "end_time must be strictly greater than start_time"})
        return data
