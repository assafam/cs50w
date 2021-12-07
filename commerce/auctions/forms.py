from django import forms
from django.forms import ModelForm
from .models import Auction, Bid

class NewAuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "description", "starting_bid", "image_url", "category"]
        widgets = {
            "description": forms.Textarea(attrs={
                "placeholder": "Description",
                "rows": "5",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            "placeholder": "Title",
            "autofocus": True,
        })
        self.fields['starting_bid'].widget.attrs.update(placeholder="Starting bid")
        self.fields['image_url'].widget.attrs.update(placeholder="Image URL (optional)")
        self.fields['category'].empty_label = "Category (optional)"

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bid'].widget.attrs.update(placeholder="Bid")
