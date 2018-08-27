from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLog, ALLOWED_CONTENT_TYPES


class CommentListSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'created_at', 'text', 'author_id', 'parent_id')

    def get_parent_id(self, obj):
        if obj.parent_type_id == ContentType.objects.get_for_model(Comment).id:
            return obj.parent_id
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('author', 'text', 'parent_id', 'parent_type')
        extra_kwargs = {
            'parent_type': {
                'queryset': ContentType.objects.filter(model__in=ALLOWED_CONTENT_TYPES)
            }
        }

    def validate(self, data):
        content_type = data['parent_type']
        if not content_type.model_class().objects.filter(
                id=data['parent_id']).exists():
            raise serializers.ValidationError({
                'parent_id': f'{content_type.model} does not exist'
            })
        return data


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)


class CommentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLog
        fields = ('created_at', 'comment_id', 'user_id', 'event', 'changes')
