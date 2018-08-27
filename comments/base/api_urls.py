from django.conf.urls import url
from .views import (
    CommentListView, CommentDetailView, CommentDescendantsView, UserCommentListView,
    CommentListAsFileView, CommentLogView
)

urlpatterns = [
    url(r'^comments/$', CommentListView.as_view()),
    url(r'^comments/(?P<pk>\d+)/$', CommentDetailView.as_view()),
    url(r'^comments/(?P<pk>\d+)/log/$', CommentLogView.as_view()),
    url(r'^comments-descendants/$', CommentDescendantsView.as_view()),
    url(r'^user-comments/(?P<user_id>\d+)/$', UserCommentListView.as_view()),
    url(r'^comments-as-file/$', CommentListAsFileView.as_view())
]
