from django.urls import path
from . import views

urlpatterns = [
    path('', views.rooms, name='rooms'),
    path('create/', views.create_room, name='create_room'),
    
    # URLs de convite
    path('invites/', views.convite_pendente, name='convite_pendente'),
    path('invites/accept/<int:invitation_id>/', views.accept_invite, name='accept_invite'),
    path('invites/reject/<int:invitation_id>/', views.reject_invite, name='reject_invite'),
    path('invite/<int:user_id>/', views.invite_user, name='invite_user'),
    
    # URLs das salas
    path('rooms/<slug:room_slug>/kick/<int:user_id>/', views.kick_user, name='kick_user'),
    path('rooms/<slug:slug>/', views.room_detail, name='room_detail'),
    path('room/<slug:slug>/info_chat', views.chatroom_def, name = "chatroom_def"),
    

    # Editar e apagar mensagens
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
]