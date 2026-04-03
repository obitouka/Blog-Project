from django import forms                              # 0.16 django.forms→module for creating HTML forms,validation,cleaning user input
from .models import Comment                           # 8.45 '.'→current app;models→file;Comment→DB model used for ModelForm


# 11.18 EMAIL FORM FEATURE
class EmailPostForm(forms.Form):                      # 11.19 forms.Form→base class for non-model forms(manual fields,no DB binding)
    name = forms.CharField(max_length=25)             # 11.20 CharField→string input;max_length=25→limits input size;renders as <input type="text">
    email = forms.EmailField()                        # 11.21 EmailField→validates proper email format;renders as <input type="email">
    to = forms.EmailField()                           # 11.22 Receiver email field;ensures valid email before sending
    comments = forms.CharField(                       # 11.23 CharField used for message body
        required=False,                               # required=False→field can be empty(optional input)
        widget=forms.Textarea                         # widget→controls HTML rendering;Textarea→<textarea> multi-line input box
    )


# 8.46 COMMENT FORM FEATURE
class CommentForm(forms.ModelForm):                   # 8.47 ModelForm→auto-generates form fields from model definition
    class Meta:                                       # Meta class→configuration for ModelForm
        model=Comment                                # 8.48 model→connects this form to Comment model(DB table)
        fields=['name','email','body']               # 8.49 fields→only these model fields included in form (others excluded)

        # name→maps to Comment.name(CharField)→input for user name
        # email→maps to Comment.email(TextField)→input for user email
        # body→maps to Comment.body(TextField)→textarea for comment content