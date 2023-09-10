from django import forms


class MyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_data = kwargs.pop('form_data', [])
        super(MyForm, self).__init__(*args, **kwargs)

        for field_data in form_data:
            field_name = field_data['name']
            field_type = field_data['type']
            field_values = field_data['values']
            field_restrictions = field_data['restrictions']
            min_value = field_restrictions.get('min')
            max_value = field_restrictions.get('max')

            if field_type == 'dictionary':
                # Tworzenie pola z wyborem z dostępnych wartości
                self.fields[field_name] = forms.ChoiceField(
                    label=field_name,
                    choices=[(value, value) for value in field_values],
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    required=True
                )
            elif field_type == 'string':
                # Tworzenie pola tekstowego z ograniczeniami min i max
                min_value = field_restrictions.get('min')
                max_value = field_restrictions.get('max')

                self.fields[field_name] = forms.CharField(
                    label=field_name + " ( " + str(min_value) + "-" + str(max_value) + " znaków)",
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    min_length=min_value,
                    max_length=max_value
                )
            elif field_type == 'integer':
                # Tworzenie pola tekstowego z ograniczeniami min i max
                self.fields[field_name] = forms.IntegerField(
                    label=field_name + " ( " + str(min_value) + "-" + str(max_value) + " )",
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=True,
                    min_value=min_value,
                    max_value=max_value
                )
            else:
                self.fields[field_name] = forms.FloatField(
                    label=field_name + " ( " + str(min_value) + "-" + str(max_value) + " )",
                    required=True,
                    min_value=min_value,
                    max_value=max_value
                )