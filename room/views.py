from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Room, Message, Invitation
from .forms import RoomCreateForm, InviteUserForm # type: ignore
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.db.models import Q

@login_required
def kick_user(request, room_slug, user_id):
    room = get_object_or_404(Room, slug=room_slug)
    if request.user != room.dono:
        return HttpResponseForbidden("Apenas o dono consegue expulsar!")

    user_to_kick = get_object_or_404(User, id=user_id)
    if user_to_kick == room.dono:
        return HttpResponseForbidden("Impossivel expulsar o dono.")

    room.membros.remove(user_to_kick)
    return redirect('room_detail', slug=room.slug)


@login_required
def invite_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    
    # Get rooms owned by current user
    owned_rooms = Room.objects.filter(dono=request.user)
    
    if request.method == 'POST':
        form = InviteUserForm(request.POST, user=request.user)
        if form.is_valid():
            room = form.cleaned_data['room']
            if target not in room.membros.all():
                existing_invite = Invitation.objects.filter(room=room, invited_user=target, accepted=None).exists()
                if not existing_invite:
                    Invitation.objects.create(room=room, invited_user=target, invited_by=request.user)
                    messages.success(request, f"Convite enviado para {target.username} para “{room.nome}”!")
                    Message.objects.create(room=room, user=request.user, content=f"{request.user.username} convidou {target.username} para se juntar à sala!")
            return redirect('user_info', user_id=user_id)
    else:
        form = InviteUserForm(user=request.user)
    
    return render(request, 'room/invite_user.html', {
        'form': form,
        'target': target,
        'owned_rooms': owned_rooms  # Explicitly pass owned rooms
    })


@login_required
def accept_invite(request, invitation_id):
    invite = get_object_or_404(
        Invitation,
        id=invitation_id,
        invited_user=request.user
    )

    if invite.accepted is not None:
        return HttpResponseBadRequest("O convite ja foi processado.")

    # Use the model's accept method, which now handles duplicates
    invite.accept()
    messages.success(request, f"Bem vindo a {invite.room.nome}!")
    return redirect('room_detail', slug=invite.room.slug)

@login_required
def reject_invite(request, invitation_id):
    invite = get_object_or_404(Invitation, id=invitation_id, invited_user=request.user)
    
    if invite.accepted is not None:
        return HttpResponseBadRequest("O convite ja foi processado")
    
    invite.reject()
    messages.info(request, f"Recusaste o convite {invite.room.nome}.")
    return redirect('rooms')  # Or wherever you want to redirect after rejection

# room/views.py

@login_required
def convite_pendente(request):
    # mark all not-yet-viewed pending invites as viewed
    Invitation.objects.filter(
        invited_user=request.user,
        accepted=None,
        viewed=False
    ).update(viewed=True)

    # fetch *all* pending to display them
    pending = Invitation.objects.filter(
        invited_user=request.user,
        accepted=None
    ).select_related('room','invited_by')

    return render(request, 'room/convite_pendente.html', {
        'convite_pendente': pending
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.dono = request.user
            room.save()
            room.membros.add(request.user)
            return redirect('rooms')
    else:
        form = RoomCreateForm()
    return render(request, 'room/create_room.html', {'form': form})



@login_required
def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug)

    # Negar acesso se a sala for privada e o usuário não for membro
    if room.privado_def and request.user not in room.membros.all():
        return render(request, 'room/forbidden.html', status=403)

    if request.method == 'POST':
        if 'edit_room' in request.POST and request.user == room.dono:
            nome = request.POST.get('room_nome', '').strip()
            privado = 'privado_def' in request.POST

            if nome:
                room.nome = nome
                room.privado_def = privado
                room.save()
                messages.success(request, 'Sala atualizada com sucesso.')
                return redirect('room_detail', slug=room.slug)
            else:
                messages.error(request, 'O nome da sala não pode estar vazio.')

        elif 'apagar_sala' in request.POST:
            if request.user == room.dono:
                room.delete()
                messages.success(request, 'Sala excluída com sucesso.')
                return redirect('rooms')
            else:
                return HttpResponseForbidden("Apenas o dono pode apagar a sala.")

        elif 'leave_room' in request.POST:
            room.membros.remove(request.user)
            messages.success(request, 'Você saiu da sala.')
            return redirect('rooms')

    messages_list = room.messages.all()
    users = room.membros.all()
    return render(request, 'room/room.html', {
        'room': room,
        'messages': messages_list,
        'users': users
    })

@login_required
def rooms(request):
    rooms = Room.objects.filter(
        Q(dono=request.user) | 
        Q(membros=request.user)
    ).distinct()
    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def rooms(request):
    rooms = Room.objects.filter(
        Q(dono=request.user) | Q(membros=request.user)
    ).distinct()

    # count pending unviewed invites for badge
    pending_count = Invitation.objects.filter(
        invited_user=request.user,
        accepted=None,
        viewed=False
    ).count()

    return render(request, 'room/rooms.html', {
        'rooms': rooms,
        'pending_invite_count': pending_count,
    })

@login_required
def chatroom(request):
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            Message.objects.create(user=request.user, text=message_text)
        return redirect("room")

    messages = Message.objects.all()
    return render(request, "room/room.html", {"messages": messages})

@login_required
def chatroom_def(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if request.method == 'POST':
        if 'leave_room' in request.POST and request.user != room.dono:
            room.membros.remove(request.user)
            messages.success(request, 'Você saiu da sala.')
            return redirect('rooms')

    context = {
        'room': room,
        'verificar_dono': request.user == room.dono
    }

    return render(request, 'room/editar_chatroom.html', context)


@login_required
def edit_message(request, message_id):
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Mensagem não encontrada'}, status=404)
        # Only allow the author or the room owner to edit
        if request.user != message.user:
            return HttpResponseForbidden("Não tem permissão para editar esta mensagem.")
        import json
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        if not new_content:
            return JsonResponse({'error': 'Conteúdo vazio'}, status=400)
        message.content = new_content
        message.save()
        return JsonResponse({'status': 'ok', 'new_content': new_content})
    return HttpResponseNotAllowed(['POST'])

@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Mensagem não encontrada'}, status=404)
        # Only allow the author or the room owner to delete
        if request.user != message.user and request.user != message.room.dono:
            return HttpResponseForbidden("Você não tem permissão para apagar esta mensagem.")
        message.delete()
        return JsonResponse({'status': 'ok'})
    return HttpResponseNotAllowed(['POST'])



