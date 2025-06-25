from django.db import models
from django.contrib.auth.models import User
import unicodedata
import datetime

class Perfil(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não dizer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True)

    def __str__(self):
        if self.genero == 'M':
            return f'Perfil do {self.user.username}'
        elif self.genero == 'F':
            return f'Perfil da {self.user.username}'
        else:
            return f'Perfil de {self.user.username}'

    def remover_acentos(texto):
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    @property
    def idade(self):
        if self.data_nascimento:
            today = datetime.date.today()
            born = self.data_nascimento
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None


class Artist(models.Model):
    id_artista = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    imagem = models.ImageField(upload_to='artistas/', null=True, blank=True)
    favorito = models.ManyToManyField(User, related_name='artista_favorito', blank=True)

    def __str__(self):
        return self.nome or "Artista sem nome"


class ArtistaSolo(Artist):
    data_nascimento = models.DateField()
    data_falecimento = models.DateField(null=True, blank=True)


class GrupoMusical(Artist):
    data_fundacao = models.DateField(null=True, blank=True)
    data_encerramento = models.DateField(null=True, blank=True)
    integrantes = models.ManyToManyField(ArtistaSolo, related_name='grupos', blank=True)


class Album(models.Model):
    GENRE_CHOICES = [
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('classico', 'Clássica'),
        ('hip_hop', 'Hip Hop'),
        ('eletronica', 'Eletrônica'),
    ]

    id_album = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    breve_descricao = models.TextField(null=True, blank=True)
    descricao = models.TextField()
    genero = models.CharField(max_length=50, choices=GENRE_CHOICES)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_de_lancamento = models.DateField()
    imagem = models.ImageField(upload_to='albums/', null=True, blank=True)
    artista = models.ForeignKey(Artist, on_delete=models.CASCADE, default=1)
    favorito = models.ManyToManyField(User, related_name='album_favorito', blank=True)

    def __str__(self):
        return self.nome or "Álbum sem nome"


class Carrinho(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrinho_itens')
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    adicionado_a = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')
        ordering = ['-adicionado_a']

    def __str__(self):
        user = self.user.username if self.user else "Utilizador desconhecido"
        album = self.album.nome if self.album else "Álbum desconhecido"
        return f"{album} (x{self.quantidade}) - {user}"

    @property
    def total_price(self):
        return self.album.preco * self.quantidade


class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.user.username if self.user else "Utilizador desconhecido"
        return f"Pedido #{self.id} - {user} - {self.data_pedido.strftime('%Y-%m-%d')}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        album = self.album.nome if self.album else "Álbum desconhecido"
        return f"{album} x{self.quantidade}"
