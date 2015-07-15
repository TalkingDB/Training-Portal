from django import forms


CHOICES=[('mass_input', 'Mass Input')]

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes', required=True
    )
    only_1st_restaurant= forms.BooleanField(required=False)
    for_matching_algo= forms.BooleanField(required=False)


    def clean_docfile(self):
        value = self.cleaned_data['docfile']
        if not value.name.endswith('.csv'):
            raise forms.ValidationError(u'Only csv')
