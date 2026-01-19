from django.shortcuts import render

# v2.1 
#Add Create and Update Views to list of imported generic forms.
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
from .models import Customer, Product, Order, OrderDetail
from django.db import models
# Add imports from forms to be able to create forms using forms classes.
from .forms import CustomerForm, ProductForm


# v3.0 Added Plotly Imports 
# use either graphs or express based on the kind of plot and lkevel of customization needed.
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# plot allows generating plots in html components including divs.
from plotly.offline import plot

from django.http import JsonResponse
from django.db.models import Count, F, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import ExtractYear, Cast, ExtractMonth

def DjTradersHome(request):
    return render(request,'DjTraders/index.html',{})    

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
      customer = self.get_object()
      suggested_products = customer.suggest_products_for_customer()
      suggest_offers = customer.suggest_offers_for_customers()
      context['SuggestedProducts'] = suggested_products
      context['SuggestOffers'] = suggest_offers
      return context
  
#   def suggested_products(self):    

#     customer = self.get_object()
                
#     customer = Customer.objects.get(customer_id=customer.customer_id)
#     print(customer)
#     # Get suggested products
#     suggested_products = customer.suggest_products_for_customer(customer.customer_id)

#     return suggested_products

# v3.1 Added
# Return a partial view of the Customer's Orders Placed.
def OrdersPlaced(request, selOrderYear=""):
    
    str_id = request.GET.get('customer_id')
    id=int(str_id)
    selOrderYear = request.GET.get('selOrderYear')
              
    customer = Customer.objects.get(customer_id=id)
    OrderYears = Order.AllOrderYears()

    return render(request, 'DjTraders/_OrdersPlaced.html', 
                  {
                      'customer': customer,
                      'selOrderYear': selOrderYear,
                      'OrderYears': OrderYears,
                  })

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
        
    
    TheAnnualOrders = customer.AnnualOrders()
    ordersByDatePlot = customer.OrdersPlacedPlot(selOrderYear)
    
    return render(
        request, 
        'DjTraders/_OrdersByDate.html', 
        {
            'customer': customer,
            'selOrderYear': selOrderYear,
            'OrderYears': OrderYears,
            'OrdersByDatePlot': ordersByDatePlot,
            'AnnualOrdersPlot': TheAnnualOrders,
        }
    )
    
# v3.2 Orders By Product Plot 
def OrdersByProduct(request):
    
    # extract the customer_id and selected Order Year from the request.
    # the customer ID is converted to integer from the default string for I/O
    str_customer_id = request.GET.get('customer_id')
    customer_id=int(str_customer_id)
    
    #use the customer_id to get the right customer.
    customer = Customer.objects.get(customer_id=customer_id)

    TheProductsRevenuePlot = customer.ProductReveues()
    TheProductsPlot = customer.ProductsSoldPlot()
    
    return render(
        request, 
        'DjTraders/_OrdersByProduct.html', 
        {
            'customer': customer,
            'ProductsPlot': TheProductsPlot,
            'ProductsRevenuePlot': TheProductsRevenuePlot,
        }
    )

# v3.2 Orders By Category Plot 
def OrdersByCategory(request):
    
    # extract the customer_id and selected Order Year from the request.
    # the customer ID is converted to integer from the default string for I/O
    str_customer_id = request.GET.get('customer_id')
    customer_id=int(str_customer_id)
    
    #use the customer_id to get the right customer.
    customer = Customer.objects.get(customer_id=customer_id)

    TheCategoryPlot = customer.ProductCategorySalesPlot()
    TheCategoryRevenusPlot = customer.ProductCategoryRevenusPlot()
    
    return render(
        request, 
        'DjTraders/_OrdersByCategory.html', 
        {
            'customer': customer,
            'CategoryRevenuesPlot': TheCategoryRevenusPlot,
            'CategoryPlot': TheCategoryPlot,
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


# Product class
class DjTradersProductsView(ListView):
    model = Product
    template_name = 'DjTraders/products.html'
    context_object_name = 'products'

    def all_categories(self):
        return self.model.objects.values('category__category_name').distinct().order_by('category__category_name')
    
    def get_queryset(self):
        productNameQuery = self.request.GET.get('srchProductName', '')
        categoryQuery = self.request.GET.get('srchProductCategory', '')
        price_filter = self.request.GET.get('price_filter')
        price_value = self.request.GET.get('price_value')

        if productNameQuery:
            products = self.model.objects.filter(product_name__icontains = productNameQuery)
        elif categoryQuery:
            products = self.model.objects.filter(category__category_name__icontains = categoryQuery) 
        elif price_filter == "greater":
            products = self.model.objects.filter(price__gt = price_value)
        elif price_filter == "less":
            products = self.model.objects.filter(price__lt = price_value)          
        else:
            products = self.model.objects.all()
                
        return products.order_by("product_name")
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)

        srchTermProductName = self.request.GET.get('srchProductName', '')
        srchTermProductCategory = self.request.GET.get('srchProductCategory', '')

        context["srchProductName"] = srchTermProductName
        context["srchProductCategory"] = srchTermProductCategory

        context['categories'] = self.all_categories()
        context['price_filter'] = self.request.GET.get('price_filter', '')
        context['price_value'] = self.request.GET.get('price_value', '')

        return context

class DjTradersProductDetailView(DetailView):
    model=Product
    template_name='DjTraders/productDetail.html'
    context_object_name='product'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['getCustomers'] = self.object.PurchasedBy()
        return context
    
class DjTradersProductCreate(CreateView):
    template_name="DjTraders/product_form.html"
    model=Product
    form_class = ProductForm
    success_url = '/DjTraders/Products'
    
    
class DjTradersProductEdit(UpdateView):
    model=Product
    form_class = ProductForm
    success_url = '/DjTraders/Products'  

class DjTradersProductPurchaseSummaryView(DetailView):
    model = Product
    template_name = 'DjTraders/productPurchaseDetail.html'
    context_object_name = 'product'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        purchase_summary = product.customer_orders_purchased()
        context['purchase_summary'] = purchase_summary
        return context  

class ProductAnalysisPageView(DetailView):
    model=Product
    template_name='DjTraders/productAnalysisPage.html'
    context_object_name='product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['ProductsSalePlot'] = product.AnnualProductOrders()
        #context['ProductsMonthlySales'] = self.ProductsMonthlySale()
        return context
    
def ProductsMonthlySale(request, selOrderYear=None):
        
    str_id = request.GET.get('product_id')
    print('str_id: ', str_id)
    id=int(str_id)
            
    product = Product.objects.get(product_id=id)

    selOrderYear = request.GET.get('selOrderYear')

    # To fill the dropdown, ask the Order Model for all distinct Years an Order was placed BY ANY customer.
    OrderYears = Order.AllOrderYears()

    ProductsMonthlySalePlot = product.ProductsMonthlySalePlot(selOrderYear)

    return render(request, 'DjTraders/_ProductsMonthlySale.html', 
                {
                    'product': product,
                    'selOrderYear': selOrderYear,
                    'OrderYears': OrderYears,
                    'ProductsMonthlySalePlot': ProductsMonthlySalePlot
                }) 

def ProductsSaleAnalysisByCategory(request):
    
    str_id = request.GET.get('product_id')
    print('str_id: ', str_id)
    id=int(str_id)
            
    product = Product.objects.get(product_id=id)

    TheProductCategorySalesPlot = product.ProductAnalysisCategorySalesPlot()
    TheProductCategoryRevenusPlot = product.ProductAnalysisCategoryRevenusPlot()
    
    return render(
        request, 
        'DjTraders/_ProductAnalysisByCategory.html', 
        {
            'product': product,
            'productCategorySalesPlot': TheProductCategorySalesPlot,
            'productCategoryRevenusPlot': TheProductCategoryRevenusPlot,
        }
    )

def ProductSalesAnalysis(request, pk):

    # str_id = request.GET.get('product_id')
    # print('str_id: ', str_id)
    # id=int(str_id)

    product = Product.objects.get(pk=pk)
   
    OrderYears = Order.AllOrderYears()  
    selOrderYear = request.GET.get('selOrderYear')
 
    total_sales_data = []
    if selOrderYear:
        orders = Order.objects.filter(orderdetail__product=product, order_date__year=selOrderYear)
    else:
        orders = Order.objects.filter(orderdetail__product=product)
 
    annual_data = orders.annotate(
        year=ExtractYear('order_date')
        ).values('year').annotate(
        total_orders=Count('order_id'),
        total_products_sold=Sum('orderdetail__quantity'),
        total_revenue=Sum(
            ExpressionWrapper(
                F('orderdetail__quantity') * F('orderdetail__product__price'),
                output_field=DecimalField()
            )
        )
    ).order_by('year')
 
    for year_data in annual_data:
        year = year_data['year']
        total_orders = year_data['total_orders']
        total_products_sold = year_data['total_products_sold']
        total_revenue = year_data['total_revenue']
 
        monthly_sales_data = []
       
    # Monthly sales data
        monthly_data = orders.filter(order_date__year=year).annotate(
        month=ExtractMonth('order_date')
        ).values('month').annotate(
        total_orders_month=Count('order_id'),
        total_products_sold_month=Sum('orderdetail__quantity'),
        total_revenue_month=Sum(
            ExpressionWrapper(
                F('orderdetail__quantity') * F('orderdetail__product__price'),
                output_field=DecimalField()
            )
        )
        ).order_by('month')
 
        avg_sales_data = {
            'avg_orders': total_orders / 12,
            'avg_products_sold': total_products_sold / 12,
            'avg_revenue': total_revenue / 12,
        }
 
        for month_data in monthly_data:
            month = month_data['month']
            total_orders_month = month_data['total_orders_month']
            total_products_sold_month = month_data['total_products_sold_month']
            total_revenue_month = month_data['total_revenue_month']
 
            # Compare monthly sales with average
            comparison = {
                'orders_vs_avg': total_orders_month - avg_sales_data['avg_orders'],
                'products_sold_vs_avg': total_products_sold_month - avg_sales_data['avg_products_sold'],
                'revenue_vs_avg': total_revenue_month - avg_sales_data['avg_revenue'],
            }
 
            monthly_sales_data.append({
                'month': month,
                'total_orders_month': total_orders_month,
                'total_products_sold_month': total_products_sold_month,
                'total_revenue_month': total_revenue_month,
                'comparison': comparison,
            })
 
        total_sales_data.append({
            'year': year,
            'total_orders': total_orders,
            'total_products_sold': total_products_sold,
            'total_revenue': total_revenue,
            'monthly_sales': monthly_sales_data,
            'avg_sales': avg_sales_data
        })
 
    # Prepare data for Plotly charts
    df_annual = pd.DataFrame(total_sales_data)
    df_annual['year'] = df_annual['year'].astype(int)
    df_annual['total_orders'] = pd.to_numeric(df_annual['total_orders'], errors='coerce')
    df_annual['total_revenue'] = pd.to_numeric(df_annual['total_revenue'], errors='coerce')
    df_annual['total_products_sold'] = pd.to_numeric(df_annual['total_products_sold'], errors='coerce')
   
    fig_annual = px.bar(df_annual, x='year', y=['total_orders', 'total_revenue', 'total_products_sold'],
                    title=f"Annual Sales for {product.product_name}")
    annual_chart_html = fig_annual.to_html(full_html=False)
 
 
    # Prepare monthly sales comparison chart
    df_monthly = pd.DataFrame([{
        'Month': month_data['month'],
        'Orders': month_data['total_orders_month'],
        'Revenue': month_data['total_revenue_month'],
        'Comparison with Avg': month_data['comparison']['revenue_vs_avg']
    } for year_data in total_sales_data for month_data in year_data['monthly_sales']])
   
    df_monthly['Month'] = df_monthly['Month'].astype(int)
    df_monthly['Orders'] = pd.to_numeric(df_monthly['Orders'], errors='coerce')
    df_monthly['Revenue'] = pd.to_numeric(df_monthly['Revenue'], errors='coerce')
    df_monthly['Comparison with Avg'] = pd.to_numeric(df_monthly['Comparison with Avg'], errors='coerce')
 
    fig_monthly = px.line(df_monthly, x='Month', y='Revenue', title=f"Monthly Sales Comparison for {product.product_name}")
    monthly_chart_html = fig_monthly.to_html(full_html=False)
 
 
    context = {
        'product': product,
        'ProductAnnualySalesPlot': annual_chart_html,
        'ProductMonthlySalesPlot': monthly_chart_html,
        'OrderYears': Order.objects.all().values('order_date').distinct(),
        'selOrderYear': selOrderYear,
        'OrderYears': OrderYears,
    }
 
    return render(request, 'DjTraders/_ProductSalesAnalysis.html', context)

def plot_top_bottom_revenue_products(request, selOrderYear=None):

    OrderYears = Order.AllOrderYears() 
 
    selOrderYear = request.GET.get('selOrderYear', selOrderYear)
 
    order_details_with_revenue = OrderDetail.objects.annotate(
        revenue=F('product__price') * F('quantity'),  # Calculate revenue
        year=ExtractYear('order__order_date')         # Extract year
    )
 
    if selOrderYear:
        order_details_with_revenue = order_details_with_revenue.filter(year=selOrderYear)

    revenue_per_product_year = order_details_with_revenue.values(
        'product__product_id', 'product__product_name', 'year'
    ).annotate(
        total_revenue=Sum('revenue')
    ).order_by('-total_revenue')  
 
    top_10 = list(revenue_per_product_year[:10])  # Top 10
    bottom_10 = list(revenue_per_product_year[::-1][:10])  # Bottom 10
 
    def generate_bar_chart(data, title, color_scale):
        df = pd.DataFrame({
            'Product': [item['product__product_name'] for item in data],
            'Total Revenue': [item['total_revenue'] for item in data]
        })
        fig = px.bar(
            df, x='Product', y='Total Revenue', title=title,
            labels={'Total Revenue': 'Revenue ($)', 'Product': 'Product Name'},
            color='Total Revenue', color_continuous_scale=color_scale
        )
        return plot(fig, output_type='div')
 
    top_10_html = generate_bar_chart(top_10, f'Top 10 Revenue-Generating Products in {selOrderYear or "All Years"}', 'Blues')
    bottom_10_html = generate_bar_chart(bottom_10, f'Bottom 10 Revenue-Generating Products in {selOrderYear or "All Years"}', 'Reds')
 
    context = {
        'top_10_plot': top_10_html,
        'bottom_10_plot': bottom_10_html,
        'selOrderYear': selOrderYear,
        'OrderYears': OrderYears,
    }

    return render(request, 'DjTraders/product_orders.html', context)

# endregion

