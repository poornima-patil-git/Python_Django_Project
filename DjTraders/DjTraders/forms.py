from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML 

from .models import Product, Customer
import re

# v2.1 Added Customer Form.
# A nice tutorial on Crispy Forms is at: https://simpleisbetterthancomplex.com/tutorial/2018/11/28/advanced-form-rendering-with-django-crispy-forms.html
class CustomerForm(forms.ModelForm):
    
    #dont need this, but illustrates another way to customize
    postal_code = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder':'5 char postal code'},
        ),
        label = 'Zip or Postal Code',
        help_text = 'Enter your Zip or Postal Code Please',         
        min_length=5,       
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('customer_name', css_class='form-group col-6'),
                Column('contact_name', css_class='form-group col-6'),
                css_class='form-row'
            ),
            'address',
            Row(
                Column('city', css_class='form-group col-6'),
                Column('postal_code', css_class='form-group col-3'),
                Column('country', css_class='form-group col-3'),
                css_class='form-row'
            ),
            
        Row(
            Column(),
            Column(
                Submit('submit', 'Save Changes',
                       css_class='btn btn-light my-2'),
                 HTML(
                    '<a class="btn btn-light my-2" href="javascript:history.back()">Cancel</a>'
                    )
           ),
           css_class=""
        ),
    )

    class Meta:
        model = Customer
        # can have additional fields on this line.
        fields = '__all__'

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'product_name',
            'price',
            'category',
            'unit',
           
            Submit('submit','Save',
                   css_class='btn btn-light m-3',
            )
        )

    class Meta:
        model = Product
        # can have additional fields on this line.
        fields = '__all__'
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        
        # Check if product_name contains numbers
        if re.search(r'\d', product_name):
            raise ValidationError('Product name should not contain numbers.')
        
        return product_name
    
    # def clean_price(self):
    #     price = self.cleaned_data.get('price')
        
    #     if (price < 0):
    #         #The specific message can be different.
    #         raise ValidationError("Product Price is never negative")
        
    #     elif (price > 100):
    #         raise ValidationError("Product Price is never more than $100.00")
        
  
  
