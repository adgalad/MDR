import json

from django import forms
from django.contrib.auth.forms import UserCreationForm

from app import models
from app.dash import Dash



# class FromControl(forms.From):
#     def __init__(self, arg):
#         super(FromControl, self).__init__()
#         self.fields
def validateAddress(address):
    data = Dash.validateaddress(address)
    if data:
        #print('Validate: ', data['isvalid'])
        return data['isvalid']
    return False

class AddPrivkey(forms.Form):
    privkey = forms.CharField(label="Private Key", max_length=52)

    def __init__(self, *args, **kwargs):
        super(AddPrivkey, self).__init__(*args, **kwargs)
        self.fields['privkey'].widget.attrs.update({'class' : 'form-control'})



class Raffle(forms.ModelForm):
    signers = forms.ModelChoiceField(queryset=models.User.objects.filter(can_sign=True))
    class Meta:
        model = models.Raffle
        widgets = {
            'description': forms.Textarea(),
            'signers': forms.Select(),
        }
        
        fields = ('name',
                  'thumbnail_url',
                  'signers',
                  'type',
                  'description')

    def __init__(self, *args, **kwargs):
        super(Raffle, self).__init__(*args, **kwargs)
        for i in self.fields:    
            self.fields[i].widget.attrs.update({'class' : 'form-control'})


class Login(forms.Form):
    
    username = forms.CharField(required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class' : 'form-control'})


class SignUp(UserCreationForm):

    class Meta():
        model = models.User
        fields = ("username","email",)
    
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class' : 'form-control'})

class EditProfile(forms.ModelForm):

    class Meta():
        model = models.User
        fields = ("email",)
    
    def __init__(self, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class' : 'form-control'})


class AddWalletAddress(forms.ModelForm):

    class Meta():
        model = models.User
        fields = ("wallet_address", "signature", "final_message")

    def __init__(self, *args, **kwargs):
        super(AddWalletAddress, self).__init__(*args, **kwargs)
        self.fields['final_message'].widget.attrs.update({'style': "display: none;"})
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class' : 'form-control'})


