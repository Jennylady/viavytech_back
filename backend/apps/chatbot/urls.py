from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.chatbot.views import ConversationFilterView, MessageChatNewView, ConversationNewView, ConversationProfileView

urlpatterns = [
    path('conversation/profile/<int:conversation_id>/',ConversationProfileView.as_view(),name="conversation_profile"),#GET
    path('conversation/list/filter/',ConversationFilterView.as_view(),name='Conversation_list_filter'),#GET
    path('conversation/new/',ConversationNewView.as_view(),name='conversation_new'),#POST
    path('messagechat/new/',MessageChatNewView.as_view(),name='message_new'),#POST
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
