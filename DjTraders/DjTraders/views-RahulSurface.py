from django.shortcuts import render

# v2.1 
#Add Create and Update Views to list of imported generic forms.
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
from .models import Customer, Product, Order

# Add imports from forms to be able to create forms using forms classes.
from .forms import CustomerForm


# v3.0 Added Plotly Imports 
# use either graphs or express based on the kind of plot and lkevel of customization needed.

import plotly.graph_objects as graphs
import plotly.express as px
import pandas as pd

# plot allows generating plots in html components including divs.
from plotly.offline import plot

from django.core.serializers import serialize
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import ExtractYear


# region Customer views.
class DjTradersCustomersView(ListView):
    model = Customer
    template_name = 'DjTraders/customers.html'
    context_object_name = 'customers'
    #paginate_by=15
    
    def all_countries(self):
        Countries = self.model.objects.all().order_by('country').distinct()
        return Countries.values('country')
    
    def get_queryset(self):
        '''
            A ListView class returns its data in the form of a query set object.
            The query set is a list of object of the model type.  
            In this case, the queryset is a list of customers.
        
            The get_queryset(self) function provides access to the query that generates the list of objects to return.add()
            The default is all the data mapped to the table.
            
            The function provides a way to customise the "query" so that you can change the data that goes to the template page.
            
            This technique is called "Overriding" and is used to customize functionality.
            Essentially, you are "overriding" or customizing the default get_queryset() method, 
            which gives you all the objects, so that you get a custom set of objects from the query.
            
            
            See: https://docs.djangoproject.com/en/5.1/topics/class-based-views/generic-display/ for more on 
            how to customize the data from shown in a ListView.
            
        '''
        
        customerQuery = self.request.GET.get('srchCustomerName', '')
        countryQuery = self.request.GET.get('srchCountry', '')
        
        if customerQuery:
            customers = self.model.objects.filter(
                customer_name__icontains=customerQuery
            )
        elif countryQuery:
            customers = self.model.objects.filter(
                country__icontains=countryQuery
            )
        else:
            customers = self.model.objects.all()
            
        return customers.order_by("customer_name")
    
    def get_context_data(self, **kwargs):
        '''
            The "get_context_data() method determines what data goes back to the template as the context object.
            
            By default, its bahvior is to return the "context_object" that you specify in the class 
            
            Like the get_query set method,you can override this method to give you specific information in the context.
            
            A context is dictionary of objects - <key, value> pairs.
            It has the context_object_name as the only item in the dictionary.
            But you can add variables to the context dictionary to send them back to the form.
            
            For example, here, we are using this method to override the default context
            by adding the add the key "CustomerName" with the value of what the user typed in as the search item.
            
            searchTermForCustomerName is the name we give to what the user types in to the CustomerName field.
            We can extract that from the request object.
            and then add it to the context [the default context_data] dictionary.
            
            After this, the context will have 2 things:
                an object called customers (the list of customers from the queryset()), and 
                a string object with key = "CustomerName", and 
                value = the searchTermForCustomerName
            
            Now, the context contains both of these and they are available to the template.
            
        '''
        
        #1. Get the default context (list of objects)
        context = super().get_context_data(**kwargs)
        
        #2. Get the value for the input field "CustomerName"
        searchTermForCustomerName = self.request.GET.get('srchCustomerName', '')
        searchTermForCountry = self.request.GET.get('srchCountry', '')
        
        #3 Add variables back to the context with the same key as the field name
        context["srchCustomerName"] = searchTermForCustomerName
        context["srchCountry"] = searchTermForCountry
        
        context['Countries'] = self.all_countries()
        
        #4. Give back the modified context dictionary.
        return context

class CustomerOrders(ListView):
    model = Customer
    template_name = 'DjTraders/customer_orders.html'
    context_object_name = 'customer_orders'
    
    def CustomerNumOrdersPlot(self):
        CustomersWithOrders = Customer.objects.all().annotate(
            nOrders = Count('order')
        ).order_by('nOrders').reverse()
        
        TopTenCustomersWithOrders = CustomersWithOrders[:10]
        nCustomers =  CustomersWithOrders[:10].count()
        
        customer_names = [0 for _ in range(nCustomers)]
        NumberOfOrdersPlaced = [0 for _ in range(nCustomers)]
        index = 0
        
        for cOrder in TopTenCustomersWithOrders:
            customer_names[index] = cOrder.customer_name
            NumberOfOrdersPlaced[index] = cOrder.nOrders
            index = index+1
        
       
        fig = px.bar(
          x= customer_names,
          y= NumberOfOrdersPlaced,
          color_continuous_scale=px.colors.sequential.Jet,
          color=NumberOfOrdersPlaced,
          labels={'color':'Number Of Orders'},
          height=600,
          width=1000,
          text_auto=True,
        )
        
        fig.update_layout(
          title = 'Top 10 Customers by Number of Orders Placed',
          xaxis_title="Customer",
          yaxis_title="Number Of Orders",
        )
        
        # More on Plotly colors is here: https://plotly.com/python/builtin-colorscales/
        
              
        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html

    def NCustomerOrders(self):
        CustomersWithOrders = Customer.objects.all().annotate(
            nOrders = Count('order')
        ).order_by('nOrders').reverse()
        
        TopTenCustomersWithOrders = CustomersWithOrders[:10].values('customer_name', 'nOrders')
        
        nCustomers =  CustomersWithOrders[:10].count()

        dFrame = pd.DataFrame(
            list(TopTenCustomersWithOrders),
            #columns=["Customer Name", "Number Of Orders"]
        )
        print(dFrame)
        
        fig = px.bar(
            dFrame,
            x= 'customer_name',
            y= 'nOrders',
            color_continuous_scale=px.colors.sequential.Jet,
            color="nOrders",
            labels={'color':'nOrders'},
            height=600,
            width=1000,
            text_auto=True,
        )
        
        fig.update_layout(
          title = 'Top 10 Customers by Number of Orders Placed',
          xaxis_title="Customer",
          yaxis_title="Number Of Orders",
        )
        
        # More on Plotly colors is here: https://plotly.com/python/builtin-colorscales/
        
              
        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html

        
    
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CustomerOrderPlot"] = self.CustomerNumOrdersPlot()
        context["NCustomerOrdersPlot"] = self.NCustomerOrders()
        return context
    
    

# region Customer Detail View with a OrdersPlaced plot
# v3.0 Added
class DjTradersCustomerDetailView(DetailView):
  model=Customer
  template_name=  'DjTraders/CustomerDetail.html'
  context_object_name='customer'
  
  # v3.0 Added
  def OrdersPlacedPlot(self):
      '''
        
        The OrdersPlacedPlot function uses the "current" customer object using the get_object() function
        
        The customer is queried for the customer's orders and extracting the number of orders, 
        as well as order id, order_date and the total for each order.        
        These are added to individual arrays, for each order.
        
        plotly express is used to create a bar chart of order totals arranged by order date.
        The plotly offline library is plot the chart in a "div" and make it available to the DetailView for the customer
        
      '''

      # for more on the "get_object()" function, see: https://docs.djangoproject.com/en/5.1/ref/class-based-views/mixins-single-object/
      
      #get the specific customer object 
      theCustomer = self.get_object()
      
      #CustomerOrders() member function returns a queryset of all orders placed by theCustomer.
      customerOrders = theCustomer.CustomerOrders()

      # Create arrays to hold data 
      number_Of_Orders = customerOrders.count()
      order_dates = [0 for _ in range(number_Of_Orders)]
      order_totals = [0 for _ in range(number_Of_Orders)]
      order_ids = [0 for _ in range(number_Of_Orders)]
      index = 0
      
      # for each order in customerOrders, extract, dates, totals and id in each order.
      for order in customerOrders:
          order_ids[index] = order.order_id
          order_dates[index] = order.order_date
          order_totals[index] = order.OrderTotal()
          index = index+1
        
      # Create the bar chart - x and y are required, 
      # others are optional formatting.
      fig = px.bar(
          x=order_dates,
          y= order_totals,
          
          color=order_ids,
          labels={'color':'Order'},
          height=500,
          text_auto=True,
      )
      
      figure_title = 'Order Totals by Date <br><sup> for '  + theCustomer.customer_name + '</sup>'
      
      # Format Chart and Axes titles 
      fig.update_layout(
          title = figure_title,
          xaxis_title="Order Date",
          yaxis_title="Order Total",
        )
      
      # Colors and formats - remove legend.
      fig.update_layout(
          coloraxis_showscale=False,
          yaxis_tickprefix = '$', 
          yaxis_tickformat = ',.2f'
        )
      
      # generate the plot with the figure embedded as a Div
      plot_html = plot(fig, output_type='div')
      
      #return the html to place in the context and display
      return plot_html
  
  def get_context_data(self, **kwargs):
      
      context = super().get_context_data(**kwargs)
     
      # Add the plot to the context to make it available to the template.
      context['OrdersPlot'] = self.OrdersPlacedPlot()
      return context

# v3.1 Added
# Return a partial view of the Customer's Orders Placed.

def OrdersPlaced(request):
    
    str_id = request.GET.get('customer_id')
    id=int(str_id)
              
    customer = Customer.objects.get(customer_id=id)

    return render(request, 'DjTraders/_OrdersPlaced.html', 
                  {'customer': customer})


# v3.2 Orders By Date Plot 
def OrdersByDate(request, selOrderYear=""):
    # extract the customer_id and selected Order Year from the request.
    # the customer ID is converted to integer from the default string for I/O
    str_customer_id = request.GET.get('customer_id')
    customer_id=int(str_customer_id)
    selOrderYear = request.GET.get('selOrderYear')
    
    #use the customer_id to get the right customer.
    customer = Customer.objects.get(customer_id=customer_id)

    # To fill the dropdown, ask the Order Model for all distinct Years an Order was placed BY ANY customer.
    OrderYears = Order.AllOrderYears()
        
    
    ordersByDatePlot = customer.OrdersPlacedPlot(selOrderYear)
    annualOrders = customer.AnnualOrders()
    
    
    return render(
        request, 
        'DjTraders/_OrdersByDate.html', 
        {
            'customer': customer,
            'OrdersByDatePlot': ordersByDatePlot,
            'AnnualOrders': annualOrders,
            'selOrderYear': selOrderYear,
            'OrderYears': OrderYears,
        }
    )
    
# endregion
     

#region Customer Create, Edit, Delete forms.

# v2.1 
# Add the view class with the model, the form class and route for a successful submission.  
class DjTradersCustomerCreate(CreateView):
    template_name="DjTraders/customer_form.html"
    model=Customer
    form_class = CustomerForm
    success_url = '/DjTraders/Customers'
    
    
class DjTradersCustomerEdit(UpdateView):
    template_name="DjTraders/customer_form.html"
    model=Customer
    form_class = CustomerForm
    success_url = '/DjTraders/Customers'

#Note - you do not need this - unless you are doing extra credit.
class DjTradersCustomerDelete(DeleteView):
    model=Customer
    success_url = '/DjTraders/Customers'
    template_name='DjTraders/customer_delete.html'

 
#endregion

#region JSON View
class CustomersListJSON(View):
    
    def get(self, request):
        
        allCustomerData = Customer.objects.all().annotate(
            nOrders = Count('order')
        ).order_by('nOrders').reverse()
            

        x = allCustomerData.values('customer_name', 'country', 'nOrders')[:10]
        
        
        CustomerData = list(x)#serialize("json", allCustomerData)
        
        # print(CustomerData)        
        return JsonResponse(CustomerData, safe=False)
# endregion

# endregion

#region Other Views

def DjTradersHome(request):
    return render(request,'DjTraders/index.html',{})

class DjTradersProductsView(ListView):
    model = Product
    template_name = 'DjTraders/products.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        query = self.request.GET.get('ProductName', '')
        if query:
            products = self.model.objects.filter(product_name__icontains = query)
        else:
            products = self.model.objects.all()
                
        return products.order_by("product_name")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        srchProductName = self.request.GET.get('ProductName', '')
        context["ProductName"] = srchProductName 
        return context      

# endregion
