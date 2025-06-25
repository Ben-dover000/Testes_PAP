from django import forms
from .models import Room

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['nome']

class InviteUserForm(forms.Form):
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        empty_label="(Escolha uma sala)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        # only rooms this user owns
        self.fields['room'].queryset = Room.objects.filter(dono=user)
