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
    class Meta:
        model = models.Raffle
        fields = ('name',
                  'isMultisig',
                  'signsRequired',
                  'MSpubkey1',
                  'MSpubkey2',
                  'MSpubkey3',
                  'MSpubkey4',
                  'MSpubkey5',
                  'MSpubkey6',
                  'signers',
                  'prizePercentage',
                  'addressProject',
                  'projectPercentage',
                  'ticketPrice',
                  'blockHeight',
                  'description')
    

    def __init__(self, *args, **kwargs):
        super(Raffle, self).__init__(*args, **kwargs)
        for i in self.fields:    
            self.fields[i].widget.attrs.update({'class' : 'form-control'})


    def clean_address(self):
        address = self.cleaned_data['address']
        data = Dash.validateaddress(address)
        if not data['isvalid']:
            raise forms.ValidationError(
                    '%s is not a valid address.'% address
                )
        return address

    def clean_blockHeight(self):
        blockHeight = self.cleaned_data['blockHeight']
        count = Dash.getblockcount()
        if count > blockHeight:
            raise forms.ValidationError(
                    'The block %d already exists.' % blockHeight
                )
        return blockHeight

        

    def clean(self):
        super().clean()
        
        project = self.cleaned_data['addressProject']
        
        if self.cleaned_data['isMultisig']:
            for i in range(1,7):
                field = 'MSpubkey' + str(i)
                address = self.cleaned_data[field]
                if not address:
                    self.add_error(field, "%s cannot be empty" % field)
                elif len(address) != 66:
                    self.add_error(field, "Invalid address '%s'" % address)
            
        if not validateAddress(project):
            self.add_error( "addressProject",
                    'Addres "%s" is invalid.' % project
                )

        jp = self.cleaned_data['prizePercentage']
        sp = self.cleaned_data['projectPercentage']
        if jp + sp > 90:
            if jp > sp:
                self.add_error("prizePercentage",
                    "Prize percentage is too high. Both, project and prize percetage, should sum 90%."
                )
            if jp <= sp:
                self.add_error("projectPercentage",
                    "Project percentage is too high. Both, project and prize percetage, should sum 90%."
                )
        elif jp + sp < 90:
            if jp <= sp:
                self.add_error("prizePercentage",
                    "Prize percentage is too low. Both, project and prize percetage, should sum 90%."
                )
            if jp > sp:
                self.add_error("projectPercentage",
                    "Project percentage is too low. Both, project and prize percetage, should sum 90%."
                )


    
    def clean_ticketPrice(self):
        if self.cleaned_data['ticketPrice'] < 0.00000001:
            raise forms.ValidationError(
                    "The amount most be greater than 0.00000001 tDash"
                )
        return self.cleaned_data['ticketPrice']

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
        fields = ("username",)
    
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)
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


