from datetime import datetime

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import HttpResponse

from .models import Comment, CommentLog, CommentsAsFileTask
from .permissions import HasChildrenPermission
from .serializers import (
    CommentCreateSerializer, CommentListSerializer, CommentUpdateSerializer, CommentLogSerializer
)


class ParentFromQueryParamsMixin(object):
    def get_parent(self):
        parent_id = self.request.query_params.get('parent', '')
        parent_type = self.request.query_params.get('parent_type', '')
        if parent_id.isdigit() and parent_type.isdigit():
            return int(parent_id), int(parent_type)
        return None


class CommentListView(ParentFromQueryParamsMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        parent = self.get_parent()
        if parent is None:
            return Comment.objects.none()
        return Comment.objects.get_children(parent)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentListSerializer


class CommentDetailView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects
    serializer_class = CommentUpdateSerializer
    permission_classes = (HasChildrenPermission,)

    def perform_update(self, serializer):
        CommentLog.push(
            event='CHANGE',
            user=self.request.user if self.request.user.is_authenticated else None,
            instance=serializer.instance,
            update=serializer.validated_data
        )
        serializer.save()

    def perform_destroy(self, instance):
        CommentLog.push(
            event='DELETE',
            user=self.request.user if self.request.user.is_authenticated else None,
            instance=instance
        )
        instance.delete()


class CommentDescendantsView(ParentFromQueryParamsMixin, generics.ListAPIView):
    serializer_class = CommentListSerializer
    pagination_class = None

    def get_queryset(self):
        parent = self.get_parent()
        if parent is None:
            return Comment.objects.none()
        return Comment.objects.get_descendants(parent)


class UserCommentListView(generics.ListAPIView):
    serializer_class = CommentListSerializer

    def get_queryset(self):
        return Comment.objects.filter(author=self.kwargs['user_id'])


class CommentListAsFileView(APIView):
    def get(self, request):
        params = self.get_params()
        if params is None:
            return Response({'error': 'Unexpected query params'}, status=400)
        created, task = CommentsAsFileTask.objects.create_task(**params)
        if created:
            return Response(status=201)
        if not task.ready:
            return Response(status=208)
        response = HttpResponse(content_type=task.file_content_type)
        response['Content-Disposition'] = f'attachment; filename="comments.{task.file_format}"'
        response.write(task.file.read())
        task.delete()
        return response

    def get_params(self):
        params = {
            'author_id': self._normalize_id(self.request.query_params.get('author', '')),
            'entity_id': self._normalize_id(self.request.query_params.get('entity', '')),
            'entity_type_id': self._normalize_id(self.request.query_params.get('entity_type', '')),
            'date_from': self._normalize_date(self.request.query_params.get('date_from')),
            'date_to': self._normalize_date(self.request.query_params.get('date_to'))
        }
        if not (params['author_id'] or params['entity_id'] and params['entity_type_id']):
            return None
        return params

    @staticmethod
    def _normalize_date(value):
        try:
            datetime.strptime(value, '%d-%m-%Y')
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _normalize_id(value):
        if value.isdigit():
            return int(value)
        return None


class CommentLogView(generics.ListAPIView):
    serializer_class = CommentLogSerializer

    def get_queryset(self):
        return CommentLog.objects.filter(comment_id=self.kwargs['pk'])
