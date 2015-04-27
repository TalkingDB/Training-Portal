from django import forms
import CuisineSelection.cuisine_selection as cuisine


def format_cuisine_for_choices():
    """
    """
    cuisines = cuisine.get_all_cuisines()
    output = []

    for c in cuisines:
        output.append((c,c))
    return output


CHOICES=[('mass_input', 'Mass Input'),
         ('line_input', 'Single Line Input')]

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes', required=True
    )
    input_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), initial="mass_input", required=True)
    only_1st_restaurant= forms.BooleanField(required=False)


    def clean_docfile(self):
        value = self.cleaned_data['docfile']
        if not value.name.endswith('.csv'):
            raise forms.ValidationError(u'Only csv')


CUISINE_CHOICES=format_cuisine_for_choices()

class CuisineForm(forms.Form):
    cuisine = forms.ChoiceField(choices=CUISINE_CHOICES, required=True)
