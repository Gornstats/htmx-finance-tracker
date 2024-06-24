from django import forms
from tracker.models import Transaction, Category

class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        widget = forms.RadioSelect()
    )
    
    # amount field - data validation
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be above $0")
        return amount
    
    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
