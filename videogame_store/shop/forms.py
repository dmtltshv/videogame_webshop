from django import forms
from .models import SellerProfile
from .models import Review

class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'description']

        from django import forms


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }