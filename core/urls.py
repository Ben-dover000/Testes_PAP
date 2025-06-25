from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('mudar_palavra-passe/', auth_views.PasswordChangeView.as_view(template_name='registos/mudar_palavra-passe.html'), name='password_change'),
    path('mudar_palavra-passe/concluido/', auth_views.PasswordChangeDoneView.as_view(template_name='registos/mudar_palavra-passe_concluido.html'), name='password_change_done'),
    path('album/<int:id_album>/', views.album_detail, name='album_detail'),
    path('album/<int:id_album>/favorito/', views.toggle_album_favorito, name='toggle_album_favorito'),
    path('artista/<int:id_artista>/', views.artista_detail, name='artista_detail'),
    path('artista/<int:id_artista>/favorito/', views.toggle_artista_favorito, name='toggle_artista_favorito'),
    path('utilizador/<int:user_id>/', views.user_info_view, name='user_info'),
    path('pesquisar/', views.pesquisa, name='pesquisar'),
    path('carrinho/', views.carrinho_detalhe, name='carrinho_detalhe'),
    path('carrinho/adicionar/<int:album_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/update/<int:item_id>/', views.update_item, name='update_item'),
    path('artista-aleatorio/', views.artista_aleatorio, name='artista_aleatorio'),
    path('album-aleatorio/', views.album_aleatorio, name='album_aleatorio'),
    path('checkout/', views.checkout, name='checkout'),
    path('sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('historico/', views.historico_compras, name='historico_compras'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

