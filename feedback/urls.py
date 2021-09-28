from django.urls import path

from . import views


app_name = 'feedback'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='list'),
    path('tema/<str:slug>/', views.TopicDetailView.as_view(), name='detail'),
    path('tema/<str:slug>/historico/', views.HistoryView.as_view(), name='history'),
    path('votar/<int:pk>/', views.CommentVoteView.as_view(), name='vote'),
    path('opinar/<str:slug>/', views.CreateCommentView.as_view(), name='comment'),
    path('desopinar/<int:pk>/', views.DeleteCommentView.as_view(), name='comment_delete'),
    path('postura/', views.CreateOfficialPositionView.as_view(), name='position_create'),
    path('punto-debate/', views.CreateTopicPointView.as_view(), name='point_create'),
]
