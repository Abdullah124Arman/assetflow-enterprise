from rest_framework import serializers
from .models import Allocation, TransferRequest

class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = [
            'id', 'asset_id', 'holder_type', 'holder_id', 'allocated_date',
            'expected_return_date', 'actual_return_date', 'status',
            'checkin_notes', 'created_at'
        ]
        read_only_fields = ['id', 'allocated_date', 'actual_return_date', 'status', 'created_at']

    def validate(self, data):
        # Additional validation can be added here
        return data


class TransferRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRequest
        fields = [
            'id', 'asset_id', 'from_holder_id', 'to_holder_id', 'requested_by',
            'reason', 'status', 'approved_by', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'requested_by', 'status', 'approved_by', 'created_at', 'resolved_at']
