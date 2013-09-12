# -*- coding: utf-8 -*-
from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 3 megabytes'
    )
    docdesc = forms.CharField(
        label='Description',
        max_length=300, 
        help_text='300 characters max.',
        widget=forms.Textarea
    )

class DocumentSearchForm(forms.Form):
    query = forms.CharField(
        label='Search'
    )
    
class DocumentDownloadForm(forms.Form):
    docfile = forms.FileField(
        label='Search'
    )
