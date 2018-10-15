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
    # signers = forms.ModelChoiceField(queryset=models.User.objects.filter(can_sign=True))
    class Meta:
        model = models.Raffle
        widgets = {
            'description': forms.Textarea(),
            # 'signers': forms.Select(),
        }
        
        fields = ('name',
                  'thumbnail_url',
                  # 'signers',
                  'type',
                  'description')

    def clean_thumbnail_url(self):
        url = self.cleaned_data['thumbnail_url']
        
        if url == '' or url == None:
            return '/static/img/placeholder.png'
        else:
            import requests
            from PIL import Image
            from io import StringIO, BytesIO
            r = requests.get(url)
            try:
                im = Image.open(StringIO(r.content))
            except:
                im = None

            if not im:
                try:
                    im = Image.open(BytesIO(r.content))
                except:
                    raise form.ValidationError("A valid image URL is required.")

            return self.cleaned_data['thumbnail_url']


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
    user_pk = forms.IntegerField()
    class Meta():
        model = models.User
        fields = ("wallet_address", "signature", "final_message", "public_key", "user_pk")

    def __init__(self, *args, **kwargs):
        super(AddWalletAddress, self).__init__(*args, **kwargs)
        self.fields['final_message'].widget.attrs.update({'style': "display: none;"})
        self.fields['user_pk'].widget.attrs.update({'style': "display: none;"})
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class' : 'form-control'})

    def clean(self):
        address = self.cleaned_data['wallet_address']
        signature = self.cleaned_data['signature']
        finalMessage = self.cleaned_data['final_message']
        public_key = self.cleaned_data['public_key']
        user = models.User.objects.get(pk=self.cleaned_data['user_pk'])
        validation = Dash.validateaddress(address)

        if models.User.objects.filter(wallet_address=address).exists():
            print('This address is already in use. Please use a different Dash address.', models.User.objects.filter(wallet_address=address))
            raise forms.ValidationError('This address is already in use. Please use a different Dash address.')

        if user.message != finalMessage:
            print("The signed message you entered is invalid.")
            raise forms.ValidationError("The signed message you entered is invalid.")
        
        if validation['isvalid']:
            if validation['isscript']:
                print("The address can not be a script address.")
                raise forms.ValidationError("The address can not be a script address.")
            if not validation['iswatchonly'] or not 'pubkey' in validation:
                try:
                    Dash.importpubkey(public_key, label=user.username)
                except:
                    print("The public key is invalid. Please try again.")
                    raise forms.ValidationError("The public key is invalid. Please try again.")
               
                validation = Dash.validateaddress(address)
                if not validation['iswatchonly']:
                    print('The public key you entered doesn\'t correspond to the address.')
                    raise forms.ValidationError('The public key you entered doesn\'t correspond to the address.')
                elif not 'pubkey' in validation:
                    print("Couldn't find public key.")  
                    raise forms.ValidationError("Couldn't find public key.")  
                elif not (validation['pubkey'] == public_key if pubkeyExists else False):
                    print('The public key you entered doesn\'t correspond to the address')
                    raise forms.ValidationError('The public key you entered doesn\'t correspond to the address')

            if validation['pubkey'] != public_key:
                print("The public key you entered is invalid.")
                raise forms.ValidationError("The public key you entered is invalid.")

        else:
            print("The address you entered is not valid.")
            raise forms.ValidationError("The address you entered is not valid.")

        if not Dash.verifymessage(address, signature, finalMessage):
            raise forms.ValidationError("Couldn't verify the signed message. Please try again.")
        
        


class ChangeEmailForm(forms.Form):
 email = forms.EmailField(label=("Email"), max_length=254)

 def clean_email(self):
   return self.cleaned_data['email'].lower()

 def __init__(self, *args, **kwargs):
   super(ChangeEmailForm, self).__init__(*args, **kwargs)
   for i in self.fields:
       self.fields[i].widget.attrs.update({'class' : 'form-control', 'placeholder': self.fields[i].label})
