from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.forum.views import (PublicationForumListView,PublicationForumFilterView,MessageDFNewView,MessageDFProfileView,
                              LikeMessageDFView,DislikeMessageDFView,MessageDFResponseView, MessageDFCommentView, PublicationForumProfileView,
                              PublicationForumNewView, LikePublicationFView, DislikePublicationFView, CommentPublicationView)

urlpatterns = [
    path('publication/list/',PublicationForumListView.as_view(),name='discussion_list'),#GET
    path('publication/filter/',PublicationForumFilterView.as_view(),name='discussion_filter'),#GET
    path('publication/profile/<int:publication_id>/', PublicationForumProfileView.as_view(),name='discussion_profile'),#GET
    path('publication/new/', PublicationForumNewView.as_view(), name="publication new"),#POST
    #path('publication/new/comment/', CommentPublicationView.as_view(), name='publication comment new'),#POST
    path('publication/new/comment/',MessageDFNewView.as_view(),name='message_new'),#POST
    path('message/new/comment/', MessageDFCommentView.as_view(), name="message_new_comment"),#POST
    path('message/response/',MessageDFResponseView.as_view(),name='message_response'),#POST
    path('message/profile/',MessageDFProfileView.as_view(),name='message_profile'),#GET
    path('message/like/<int:message_id>/',LikeMessageDFView.as_view(),name='message_like'),#PUT
    path('message/dislike/<int:message_id>/',DislikeMessageDFView.as_view(),name='message_dislike'),#PUT
    path('publication/like/<int:publication_id>/', LikePublicationFView.as_view(),name="publication_like"),#PUT
    path('publication/dislike/<int:publication_id>/',DislikePublicationFView.as_view(),name="publication_dislike"),#PUT
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
