from django.contrib.auth import login # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from .models import Album, Artist, Perfil, Carrinho, Pedido, ItemPedido
from .forms import CriarConta, PerfilForm
from random import shuffle
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.db.models import Q # type: ignore
import random
import stripe  # type: ignore
from django.conf import settings #type: ignore
from django.views.decorators.csrf import csrf_exempt #type: ignore
from django.http import JsonResponse, HttpResponseBadRequest#type:ignore

stripe.api_key = settings.STRIPE_SECRET_KEY

def pesquisa(request):
    query = request.GET.get('q', '').strip()
    album_results = []
    artist_results = []
    perfil_results = []

    if query:
        album_results = Album.objects.filter(nome__istartswith=query)
        artist_results = Artist.objects.filter(nome__istartswith=query)
        perfil_results = Perfil.objects.filter(
            Q(user__username__istartswith=query)
        ).select_related('user')

    context = {
        'query': query,
        'album_results': album_results,
        'artist_results': artist_results,
        'perfil_results': perfil_results,
    }
    return render(request, 'core/resultado_pesquisa.html', context)

@login_required
def user_info_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    return render(request, 'core/info_utilizador.html', {'user_obj': user_obj})


def frontpage(request):
    albums = Album.objects.all() #Busca todos os álbuns da base de dados
    albums = list(albums)  # Converte a queryset para uma lista
    shuffle(albums)  # Aleatôriamente pega os álbuns
    albums = albums[:8]  #Apresenta apenas os primeiros 
    artistas = Artist.objects.all()  # Busca todos os artistas da base de dados
    artistas = list(artistas)  # Converte a queryset para lista
    shuffle(artistas)  # Aleatoriza os artistas
    artistas = artistas[:8]  # Apresenta os primeiros 8 artistas
    return render(request, 'core/frontpage.html', {'albums': albums, 'artistas': artistas})  #Manda os resultados (Artistas e Albuns) para a frontpage


def signup(request):
    if request.method == 'POST':
        form = CriarConta(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = CriarConta()
    
    return render(request, 'core/criar_conta.html', {'form': form})


@login_required
def perfil_view(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)

    favoritos_artista = request.user.artista_favorito.all()
    favoritos_album = request.user.album_favorito.all()

    return render(request, 'core/perfil.html', {
        'perfil_form': form,
        'favoritos_artistas': favoritos_artista,
        'favoritos_albuns': favoritos_album,
    })

def album_list(request):
    albums = Album.objects.all()
    return render(request, 'core/lista.html', {'albums': albums})

def listar_artistas(request):
    artistas = Artist.objects.all()
    return render(request, 'core/frontpage.html', {'artistas': artistas})

def artista_detail(request, id_artista):
    artista = get_object_or_404(Artist, id_artista=id_artista)

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = artista.favorito.filter(id=request.user.id).exists()

    return render(request, 'core/artista_detalhes.html', {
        'artista': artista,
        'is_favorited': is_favorited,
    })

def album_detail(request, id_album):
    album = get_object_or_404(Album, id_album=id_album)
    return render(request, 'core/album_detalhes.html', {'album': album})

@login_required
def toggle_artista_favorito(request, id_artista):
    artista = get_object_or_404(Artist, pk=id_artista)
    if request.user in artista.favorito.all():
        artista.favorito.remove(request.user)
    else:
        artista.favorito.add(request.user)
        return redirect('artista_detail', id_artista=artista.pk)
    return redirect('artista_detail', id_artista=id_artista)

@login_required
def toggle_album_favorito(request, id_album):
    album = get_object_or_404(Album, pk=id_album)
    if request.user in album.favorito.all():
        album.favorito.remove(request.user)
    else:
        album.favorito.add(request.user)
        return redirect('album_detail', id_album=album.pk)
    return redirect('album_detail', id_album=id_album)

@login_required
def adicionar_ao_carrinho(request, album_id):
    album = get_object_or_404(Album, id_album=album_id)
    # Usa 'quantidade' em vez de 'quantity'
    cart_item, created = Carrinho.objects.get_or_create(
        user=request.user,
        album=album,
        defaults={'quantidade': 1}
    )
    if not created:
        cart_item.quantidade += 1
        cart_item.save()
    return redirect('carrinho_detalhe')

@login_required
def carrinho_detalhe(request):
    itens = Carrinho.objects.filter(user=request.user).select_related('album')
    total = sum(item.total_price for item in itens)
    return render(request, 'core/carrinho.html', {
        'carrinho_itens': itens,
        'carrinho_total': total,
    })

@login_required
def remover_do_carrinho(request, item_id):
    item = get_object_or_404(Carrinho, id=item_id, user=request.user)
    item.delete()
    return redirect('carrinho_detalhe')




def artista_aleatorio(request):
    artistas = list(Artist.objects.all())
    if artistas:
        artista = random.choice(artistas)
        return redirect('artista_detail', id_artista=artista.id_artista)
    return redirect('frontpage')

def album_aleatorio(request):
    albuns = list(Album.objects.all())
    if albuns:
        album = random.choice(albuns)
        return redirect('album_detail', id_album=album.id_album)
    return redirect('frontpage')


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@csrf_exempt
def checkout(request):
    carrinho_itens = Carrinho.objects.filter(user=request.user).select_related('album')

    if not carrinho_itens:
        return redirect('carrinho_detalhe')

    line_items = []

    for item in carrinho_itens:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': item.album.nome,
                },
                'unit_amount': int(item.album.preco * 100),
            },
            'quantity': item.quantidade,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://localhost:8000/sucesso/',
        cancel_url='http://localhost:8000/cancelado/',
    )

    return redirect(session.url, code=303)


@login_required
def pagamento_sucesso(request):
    carrinho_itens = Carrinho.objects.filter(user=request.user).select_related('album')
    
    if carrinho_itens.exists():
        pedido = Pedido.objects.create(user=request.user)
        for item in carrinho_itens:
            ItemPedido.objects.create(
                pedido=pedido,
                album=item.album,
                quantidade=item.quantidade,
                preco_unitario=item.album.preco
            )
        # Apaga o carrinho após criar pedido
        carrinho_itens.delete()
    
    return render(request, 'core/pagamento_sucesso.html')



@login_required
def pagamento_cancelado(request):
    return render(request, 'core/pagamento_cancelado.html')


@login_required
def historico_compras(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-data_pedido').prefetch_related('itens__album')
    return render(request, 'core/historico_compras.html', {'pedidos': pedidos})



@login_required
def update_item(request, item_id):
    if request.method == 'POST':
        try:
            quantidade = int(request.POST.get('quantidade'))
            item = Carrinho.objects.get(id=item_id, user=request.user)
            item.quantidade = quantidade
            item.save()
            return JsonResponse({'status': 'ok', 'novo_total': item.total_price})
        except Carrinho.DoesNotExist:
            return HttpResponseBadRequest("Item não encontrado.")
        except Exception as e:
            return HttpResponseBadRequest(f"Erro: {e}")
    return HttpResponseBadRequest("Método não permitido.")
