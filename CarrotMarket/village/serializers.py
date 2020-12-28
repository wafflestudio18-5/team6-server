from rest_framework import serializers

from village.models import Comment

...


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'article',
            'content',
            'parent',
            'created_at',
            'updated_at',
            'deleted_at',
        )
        read_only_fields = ['user']
