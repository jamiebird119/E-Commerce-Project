from .models import Product, Category
from django import forms


class ProductForm(forms.ModelForm):
    class Meta():
        model = Product
        field = '__all__'
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get.friendly_names())for c in categories]
        self.fields['category'].choices = friendly_names
        for field, field_name in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
