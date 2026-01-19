# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from decimal import Decimal
from datetime import datetime

from django.db import models
from django.db.models.functions import ExtractYear, ExtractMonth, Cast, Coalesce
from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField, Max

import plotly.express as px
from plotly.offline import plot
import pandas as pd
from datetime import timedelta
import datetime


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255, blank=False, null=False) #required
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'customers'
     
    def __str__(self):
        return (
    		self.customer_name 
      		+ " [Contact: "+ self.contact_name +  "]"
        )

    def CustomerOrders(self):
        orders = Order.objects.all().filter(customer = self.customer_id)
        return orders
    
    def get_latest_order_date(self):
        latest_order = Order.objects.filter(customer=self).aggregate(latest_order=Max('order_date'))
        return latest_order['latest_order']

    # Assignment2: Extra Credit1: Logic for getting active customers - First we need to get the most recent order for the customer based on order_date and see if its is geater than one year and 
    # accordingly return True/False and update the database table. For database, I have added a new column named is_active.
    def is_active_customers(self):
        one_year_ago = datetime.datetime.now().date() - timedelta(days=365) 
        latest_order_date = self.get_latest_order_date()

        if latest_order_date:
            if latest_order_date > one_year_ago:
                self.is_active = True
                self.save()
                return True
            else:
                self.is_active = False
                self.save()
                return False
        else:
            return True  
    
    def NumberOfOrders(self):
        orders = Order.objects.all().filter(customer = self.customer_id)
        return orders.count()  

    # v3.2 Added - Member function in Customers class to generate Orders Plot based on supplied year
    def OrdersPlacedPlot(self, year):
   

        customerOrders = self.CustomerOrders().order_by('order_date').annotate(
          Year = ExtractYear("order_date"),
          Month = ExtractMonth("order_date"),
          CustomerName = F('customer__customer_name'),
          OrderTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity')),
          NumberOfProducts = Count('orderdetail'),
        #   ProductName = F('orderdetail__product__product_name'),
        #   CategoryName = F('orderdetail__product__category__category_name'),
        #   TotalQuantity = Sum('orderdetail__quantity'),
        #   ProductPrice = Sum('orderdetail__product__price'),
        )
        
        if year: 
            customerOrders = customerOrders.filter(Year__contains= year)

        if customerOrders.count()==0:
            return '<div> No Orders placed</div>'
        
        #print(list(customerOrders.values_list()))
        
        ordersdFrame = pd.DataFrame(
          list(customerOrders.values())
        )
        
        #print(ordersdFrame)
        
      # Create the bar chart - x and y are required, 
      # others are optional formatting.
        fig = px.bar(
            ordersdFrame,
            x='order_date',
            y= 'OrderTotal',
            color='order_id',
            labels={'color':'order_id'},
            text_auto=True,
        )
        
        figure_title = 'Orders by Date for '  + self.customer_name
      
        # Format Chart and Axes titles 
        fig.update_layout(
            title = figure_title,
            xaxis_title="",
            yaxis_title="Year Order Placed",
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

    # v3.2 Generate a list of objects for the total sales revenue from orders placed each year by the current customer - "self".
    def AnnualOrders(self):
        
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        annualOrders = self.CustomerOrders().annotate(
          Year = Cast(F("order_date__year"),output_field=models.CharField()),
          OrderTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'), 
                           distinct=True),
        ).values('Year', 'OrderTotal').order_by("Year")
        
        
        #print(annualOrders)

        #print(list(annualOrders))

        annuals =pd.DataFrame(list(annualOrders)) 
        print(annuals)
        annuals = annuals.groupby("Year").agg("sum").reset_index()
        print(annuals)

        fig = px.bar(annuals,x='Year', y='OrderTotal', 
                     color='Year', text_auto=True,
                    )

        # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Annual Orders',
            xaxis_title="Order Year",
            yaxis_title="Order Total",
        )
        
        # Colors and formats - show/hide legend.
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis_tickprefix = '$', 
            yaxis_tickformat = ',.2f'
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html

    # v3.2 Generate a plot of products and their total sales revenue from orders placed by the current customer - "self".
    def ProductReveues(self):
        
        
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        productOrders = self.CustomerOrders().order_by('order_date').annotate(
            ProductName = F('orderdetail__product__product_name'),
            CategoryName = F('orderdetail__product__category__category_name'),
            TotalQuantity = Sum('orderdetail__quantity'),
            ProductTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).distinct()

        
        productOrders = productOrders.values('ProductName', 'ProductTotal', 'CategoryName').order_by('CategoryName')


        productsData =pd.DataFrame(list(productOrders)) 
        productsData = productsData.groupby('ProductName').agg("sum").reset_index()
        print(productsData)
        
        fig = px.bar(productsData,x='ProductName', y='ProductTotal', 
                     color='ProductName', text_auto=True,                    )
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Revenues from Products',
            xaxis_title="Products",
            yaxis_title="Revenue",
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

    # v3.2 Generate a plot of products and their total sales revenue from orders placed by the current customer - "self".
    def ProductsSoldPlot(self):
        
        
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        productOrders = self.CustomerOrders().order_by('order_date').annotate(
            ProductName = F('orderdetail__product__product_name'),
            CategoryName = F('orderdetail__product__category__category_name'),
            TotalQuantity = Sum('orderdetail__quantity'),
            ProductTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).distinct()

        
        productOrders = productOrders.values('ProductName', 'ProductTotal', 'TotalQuantity')


        productsData =pd.DataFrame(list(productOrders)) 
        productsData = productsData.groupby('ProductName').agg("sum").reset_index()
        print(productsData)
        
        fig = px.bar(productsData,x='ProductName', y='TotalQuantity', 
                     color='ProductName', text_auto=True)
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Products Quantities',
            xaxis_title="Products",
            yaxis_title="Revenue",
        )
        
        # Colors and formats - remove legend.
        fig.update_layout(
            coloraxis_showscale=False,
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html

    # v3.2 Generate a plot of products and their total sales revenue from orders placed by the current customer - "self".
    def ProductCategoryRevenusPlot(self):
        
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        categoryOrders = self.CustomerOrders().order_by('order_date').annotate(
            #ProductName = F('orderdetail__product__product_name'),
            CategoryName = F('orderdetail__product__category__category_name'),
            CategoryTotalQuantity = Sum('orderdetail__quantity'),
            CategoryTotalRevenue = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).distinct()

        categoryOrders = categoryOrders.values('CategoryName', 'CategoryTotalRevenue')
       
        print(list(categoryOrders))

        categoryData =pd.DataFrame(list(categoryOrders)) 
        categoryData = categoryData.groupby("CategoryName").agg("sum").reset_index()

        print(categoryData)
        
        fig = px.bar(categoryData,x='CategoryName', y='CategoryTotalRevenue', 
                     color='CategoryName', text_auto=True,)
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Category Sales Revenues',
            xaxis_title="Category",
            yaxis_title="Sales Revenue from Category",
        )
        
        # Colors and formats - remove legend.
        fig.update_layout(
            coloraxis_showscale=False,
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html
    
    # v3.2 Generate a plot of products and their total sales revenue from orders placed by the current customer - "self".
    def ProductCategorySalesPlot(self):
        
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        categoryOrders = self.CustomerOrders().order_by('order_date').annotate(
            #ProductName = F('orderdetail__product__product_name'),
            CategoryName = F('orderdetail__product__category__category_name'),
            CategoryTotalQuantity = Sum('orderdetail__quantity'),
            #ProductTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).distinct()

        
        categoryOrders = categoryOrders.values('CategoryName', 'CategoryTotalQuantity').order_by("CategoryTotalQuantity")
       
        print(list(categoryOrders))

        categoryData =pd.DataFrame(list(categoryOrders)) 
        categoryData = categoryData.groupby("CategoryName").agg("sum").reset_index()

        print(categoryData)
        
        fig = px.bar(categoryData,x='CategoryName', y='CategoryTotalQuantity', 
                     color='CategoryName', text_auto=True,)
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Category Sales',
            xaxis_title="Category",
            yaxis_title="# of Products Bought with Category",
        )
        
        # Colors and formats - remove legend.
        fig.update_layout(
            coloraxis_showscale=False,
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html


    # Assignment3: Extra Credit2: Offer suggested products for customers based on their purchasing patterns.
    def suggest_products_for_customer(self):

        # Get products purchased by the customer
        purchased_products = OrderDetail.objects.filter(order__customer_id=self.customer_id).values_list('product_id', flat=True)

        print('purchased_products: ', purchased_products)

        # Find customers who purchased the same products
        similar_customers = OrderDetail.objects.filter(product_id__in=purchased_products).exclude(order__customer_id=self.customer_id).values_list('order__customer_id', flat=True)
        print('similar_customers: ', similar_customers)

        # Find products purchased by similar customers, excluding already purchased ones
        suggested_products = (
            Product.objects.filter(
                orderdetail__order__customer_id__in=similar_customers
            )
            .exclude(orderdetail__product_id__in=purchased_products)
            .annotate(purchase_count=Count('orderdetail'))
            .order_by('-purchase_count')[:10]  # Order by popularity
        )

        print('suggested_products: ', suggested_products)

        return suggested_products

    # Assignment3: Extra Credit3: Suggest offers to customers based on there spending 
    def suggest_offers_for_customers(self):
        annualOrders = self.CustomerOrders().annotate(
          Year = Cast(F("order_date__year"),output_field=models.CharField()),
          OrderTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'), 
                           distinct=True),
        ).values('Year', 'OrderTotal').order_by("Year")

        annuals =pd.DataFrame(list(annualOrders)) 
        annuals = annuals.groupby("Year").agg("sum").reset_index()
        print(annuals)

        latest_year = annuals.loc[annuals['Year'].idxmax()]
        print('latest_year: ', latest_year)
        latest_spending = latest_year['OrderTotal']
        print('latest_spending: ', latest_spending)

        if latest_spending >= 10000:
            current_level = 'Platinum'
            discount = 7.5
            advice = "You are already at the highest level! Keep maintaining your spending above $10,000 annually to retain Platinum status."
        elif latest_spending >= 7500:
            current_level = 'Diamond'
            discount = 5.0
            advice = f"You're at Diamond level with a 5% discount. Spend an additional ${10000 - latest_spending:.2f} this year to reach Platinum."
        elif latest_spending >= 5000:
            current_level = 'Gold'
            discount = 2.5
            advice = f"You're at Gold level with a 2.5% discount. Spend an additional ${7500 - latest_spending:.2f} this year to reach Diamond or ${10000 - latest_spending:.2f} to reach Platinum."
        else:
            current_level = 'No Discount'
            discount = 0.0
            advice = f"You currently do not qualify for a discount. Spend at least ${5000 - latest_spending:.2f} this year to achieve Gold status and start saving."

        context = {
            'latest_spending': f"${latest_spending:.2f}",
            'latest_year': latest_year['Year'],
            'current_level': current_level,
            'advice': advice,
        }
        return context  


    

#region Category, Product and Order Models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    #    category_name = models.CharField(max_length=255, blank=True, null=True)
    #blank = False, null=False => Field is required.
    category_name = models.CharField(max_length=255, blank=False, null=False)
    #Can assign a default value for fields using default.
    description = models.CharField(max_length=255, blank=True, null=True, default="")

    class Meta:
        managed = False
        db_table = 'categories'
    
    def __str__(self):
        return self.category_name
        
    
    @property
    def category(self):
        return self.category_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    unit = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    is_available = models.BooleanField(default=True)

    # Method to return the customers who purchased this product
    def PurchasedBy(self):
        CustomersWhoBoughtProduct = Customer.objects.filter(
            order__orderdetail__product_id=self.product_id
        ).distinct()
        return CustomersWhoBoughtProduct
    
    def NProductOrders(self):
        # Step 1: Calculate revenue for each order detail
        order_details_with_revenue = OrderDetail.objects.annotate(
            revenue=F('product__price') * F('quantity')  # revenue = product price * quantity
        )

        # Step 2: Aggregate revenue by product and year
        revenue_per_product_year = order_details_with_revenue.annotate(
            year=ExtractYear('order__order_date')  # Extract year from order date
        ).values('product__product_id', 'product__product_name', 'year').annotate(
            total_revenue=Sum('revenue')  # Sum of revenue for each product per year
        ).order_by('year', '-total_revenue')  # Order by year and total revenue descending

        # Step 3: Get Top and Bottom 10 products by revenue per year
        top_bottom_revenue = {}
        for year in set(item['year'] for item in revenue_per_product_year):
            # Filter data for the current year
            products_in_year = [item for item in revenue_per_product_year if item['year'] == year]

            # Get top 10 and bottom 10 products by revenue for the current year
            top_10 = products_in_year[:10]
            bottom_10 = products_in_year[-10:]

            # Store the results in a dictionary, keyed by year
            top_bottom_revenue[year] = {
                'top_10': top_10,
                'bottom_10': bottom_10
            }

        # Step 4: Calculate the overall top and bottom 10 products (across all years)
        overall_revenue_per_product = revenue_per_product_year.values(
            'product__product_id', 'product__product_name'
        ).annotate(
            total_revenue=Sum('revenue')
        ).order_by('-total_revenue')

        # Get the overall top 10 and bottom 10 products by total revenue
        overall_top_10 = overall_revenue_per_product[:10]
        overall_bottom_10 = overall_revenue_per_product[-10:]

        # Step 5: Plot the results using Plotly

        # Plot Overall Top 10 Products
        top_10_names = [product['product__product_name'] for product in overall_top_10]
        top_10_revenue = [product['total_revenue'] for product in overall_top_10]
        
        # Create a DataFrame for top 10 products
        top_10_df = pd.DataFrame({
            'Product': top_10_names,
            'Total Revenue': top_10_revenue
        })
        
        # Plot using Plotly Express
        fig = px.bar(top_10_df, x='Product', y='Total Revenue', title='Overall Top 10 Revenue-Generating Products',
                    labels={'Total Revenue': 'Revenue ($)', 'Product': 'Product Name'},
                    color='Total Revenue', color_continuous_scale='Blues')
        fig.update_layout(xaxis_tickangle=-45)
        fig.show()

        # Plot Overall Bottom 10 Products
        bottom_10_names = [product['product__product_name'] for product in overall_bottom_10]
        bottom_10_revenue = [product['total_revenue'] for product in overall_bottom_10]
        
        # Create a DataFrame for bottom 10 products
        bottom_10_df = pd.DataFrame({
            'Product': bottom_10_names,
            'Total Revenue': bottom_10_revenue
        })
        
        # Plot using Plotly Express
        fig = px.bar(bottom_10_df, x='Product', y='Total Revenue', title='Overall Bottom 10 Revenue-Generating Products',
                    labels={'Total Revenue': 'Revenue ($)', 'Product': 'Product Name'},
                    color='Total Revenue', color_continuous_scale='Reds')
        fig.update_layout(xaxis_tickangle=-45)
        fig.show()

    # 2A - Monthly Sales Analysis
    def ProductsMonthlySalePlot(self, year):
   
        productOrders = OrderDetail.objects.filter(product=self).annotate(
                Year=Cast(F("order__order_date__year"),output_field=models.CharField()),         # Extract year
                Month=ExtractMonth("order__order_date"),
                OrderTotal=Sum(F('product__price') * F('quantity'), distinct=True)  # Calculate revenue
        ).values('Year', 'Month', 'OrderTotal').order_by('Month')

        if year: 
            productOrders = productOrders.filter(Year__contains= year)

        if productOrders.count()==0:
            return '<div> No Orders placed</div>'
        
        #print(list(customerOrders.values_list()))
        
        ordersdFrame = pd.DataFrame(
          list(productOrders.values())
        )
        
        #print(ordersdFrame)
        
      # Create the bar chart - x and y are required, 
      # others are optional formatting.
        fig = px.bar(
            ordersdFrame,
            x='Month',
            y= 'OrderTotal',
            color='order_id',
            labels={'color':'order_id'},
            text_auto=True,
        )
        
        figure_title = 'Orders by Date for '  + self.product_name
      
        # Format Chart and Axes titles 
        fig.update_layout(
            title = figure_title,
            xaxis_title="",
            yaxis_title="Year Order Placed",
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
        
  
    # 2A - Annual Sales Analysis
    def AnnualProductOrders(self):

        annualProductOrders = OrderDetail.objects.filter(product=self).annotate(
                Year=Cast(F("order__order_date__year"),output_field=models.CharField()),         # Extract year
                OrderTotal=Sum(F('product__price') * F('quantity'), distinct=True)  # Calculate revenue
        ).values('Year', 'OrderTotal').order_by('Year')

        #print(annualOrders)

        #print(list(annualOrders))

        annuals =pd.DataFrame(list(annualProductOrders)) 
        print(annuals)
        annuals = annuals.groupby("Year").agg("sum").reset_index()
        print(annuals)
        
        fig = px.bar(annuals,x='Year', y='OrderTotal', 
                     color='Year', text_auto=True,
                    )

        # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Annual Orders',
            xaxis_title="Order Year",
            yaxis_title="Order Total",
        )
        
        # Colors and formats - show/hide legend.
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis_tickprefix = '$', 
            yaxis_tickformat = ',.2f'
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html
    
    # 2C - Product Sales Analysis
    def total_sales(self, year=None):
        #orders = self.orderdetail_set.all()
        orders = Order.objects.all()
 
        if year:
            orders = orders.filter(order__order_date__year=year)
 
        total_quantity = orders.aggregate(
            total_quantity=Coalesce(Sum('quantity'), 0)
        )['total_quantity']
 
        total_revenue = orders.aggregate(
            total_revenue=Coalesce(Sum(F('quantity') * F('product__price')), 0)
        )['total_revenue']
 
        return total_quantity, total_revenue

    # 2D - Product Analysis Category Revenue Plot
    def ProductAnalysisCategoryRevenusPlot(self):
        
        categoryOrders = OrderDetail.objects.filter(product=self).annotate(
            #ProductName = F('orderdetail__product__product_name'),
            CategoryName = F('product__category__category_name'),
            CategoryTotalQuantity = Sum('quantity'),
            CategoryTotalRevenue = Sum(F('product__price')*F('quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).distinct().order_by('order__order_date')

        categoryOrders = categoryOrders.values('CategoryName', 'CategoryTotalRevenue')
       
        print(list(categoryOrders))

        categoryData =pd.DataFrame(list(categoryOrders)) 
        categoryData = categoryData.groupby("CategoryName").agg("sum").reset_index()

        print(categoryData)
        
        fig = px.bar(categoryData,x='CategoryName', y='CategoryTotalRevenue', 
                     color='CategoryName', text_auto=True,)
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Product Sales Revenues',
            xaxis_title="Category",
            yaxis_title="Sales Revenue from Category",
        )
        
        # Colors and formats - remove legend.
        fig.update_layout(
            coloraxis_showscale=False,
        )


        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html


    # 2D - Product Analysis Category Sales Plot
    def ProductAnalysisCategorySalesPlot(self):
          
        # Year is extracted from order_date using the "__" for year ()
        # This is another method to get components of a datetime object, in addition to the "ExtractYear" function
        categoryOrders = OrderDetail.objects.filter(product=self).annotate(
            CategoryName = F('product__category__category_name'),
            CategoryTotalQuantity = Sum('quantity'),
            #ProductTotal = Sum(F('orderdetail__product__price')*F('orderdetail__quantity'),distinct=True),
            #Year = Cast(F("order_date__year"), output_field=models.CharField()),
        ).order_by('order__order_date')

        
        categoryOrders = categoryOrders.values('CategoryName', 'CategoryTotalQuantity').order_by("CategoryTotalQuantity")
       
        print(list(categoryOrders))

        categoryData =pd.DataFrame(list(categoryOrders)) 
        categoryData = categoryData.groupby("CategoryName").agg("sum").reset_index()

        print(categoryData)
        
        fig = px.bar(categoryData,x='CategoryName', y='CategoryTotalQuantity', 
                     color='CategoryName', text_auto=True,)
                # Format Chart and Axes titles 
        fig.update_layout(
            title = 'Product Sales',
            xaxis_title="Category",
            yaxis_title="Products Bought with Category",
        )
        
        # Colors and formats - remove legend.
        fig.update_layout(
            coloraxis_showscale=False,
        )

        # generate the plot with the figure embedded as a Div
        plot_html = plot(fig, output_type='div')
        
        #return the html to place in the context and display
        return plot_html


    # Extra Credit2: 
    def customer_orders_purchased(self):
        order_purchase_summary = OrderDetail.objects.filter(product=self).values('order__customer__customer_name').annotate(
            total_quantity=Sum('quantity'),
            total_orders=Count('order')
        )


        return order_purchase_summary
    
    # Extra Credit1: 
    def get_latest_order_date(self):
        latest_order = OrderDetail.objects.filter(product=self).aggregate(latest_order_date=Max('order__order_date'))
        return latest_order['latest_order_date']
 
    def get_availabilityStatus(self):
        one_year_ago = datetime.datetime.now().date() - timedelta(days=365)
        latest_order_date = self.get_latest_order_date()
 
        if latest_order_date:
            if latest_order_date > one_year_ago:
                self.is_available = True
                self.save()
                return "Available"
            else:
                self.is_available = False
                self.save()
                return "Unavailable"
        else:
            return True

    class Meta:
        managed = True
        db_table = 'products'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    #customer_id = models.IntegerField(blank=True, null=True)
    # I am not using on_delete=models.Cascade because I dont want to delete customers when an order is deleted.
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    # The order date will be added for the current date when the order is saved.
    order_date = models.DateField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'orders'
    
    def AllOrderDetails(self):
        orderdetails = OrderDetail.objects.filter(order = self.order_id)
        return orderdetails
    
    def OrderTotal(self):
        orderDetails = OrderDetail.objects.filter(order = self.order_id)
        total = Decimal("0.0")
        
        for line in orderDetails:
            total += line.Total #(quantity*product.price)
        return total
    
    def AllOrderYears():
        '''
            Returns a queryset of each distinct year an order was placed, 
            in chronological order
        '''
        allYears = Order.objects.all().annotate(
            Year = ExtractYear('order_date')
        ).order_by('Year').distinct()
        
        return allYears.values('Year')

class OrderDetail(models.Model):
    order_detail_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_details'
    
    @property
    def Total(self):
        return self.quantity*self.product.price
    
    @property
    def product_name(self):
        if (self.product):
            return self.product.product_name
        else:
            return ''

#endregion
