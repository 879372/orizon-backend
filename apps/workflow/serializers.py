from rest_framework import serializers
from .models import FlowNode, FlowEdge, FlowNodeItem


class FlowNodeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowNodeItem
        fields = ['id', 'node', 'label', 'is_done', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'node': {'required': False}
        }


class FlowNodeSerializer(serializers.ModelSerializer):
    items = FlowNodeItemSerializer(many=True, read_only=True)
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = FlowNode
        fields = [
            'id', 'project', 'title', 'description', 'status',
            'position_x', 'position_y', 'color', 'order',
            'items', 'is_blocked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'project': {'required': False}
        }

    def get_is_blocked(self, obj):
        return obj.is_blocked_by_dependencies()


class FlowEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowEdge
        fields = ['id', 'project', 'source', 'target', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'project': {'required': False}
        }

    def validate(self, attrs):
        source = attrs.get('source')
        target = attrs.get('target')
        if source and target and source == target:
            raise serializers.ValidationError("Um nó não pode depender de si mesmo.")
        return attrs
