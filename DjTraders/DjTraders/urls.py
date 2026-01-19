
from django.urls import path
from . import views

urlpatterns = [
    path(
        'DjTraders', 
        views.DjTradersHome, 
        name='DjTraders.Home'),

    path(
        'DjTraders/Customers', 
         views.DjTradersCustomersView.as_view(), 
         name='DjTraders.Customers'),

    path(
        'DjTraders/CustomersJSON', 
         views.CustomersListJSON.as_view(), 
         name='DjTraders.CustomersJSON'),
    
    path(
        'DjTraders/TopTenCustomers', 
         views.CustomerOrders.as_view(), 
         name='DjTraders.TopCustomerOrders'),
    

    # v2.1 
    # Add path to Form for add and edit customers
    path(
        route = 'DjTraders/Customers/new', 
        view = views.DjTradersCustomerCreate.as_view(), 
        name='DjTraders.CustomerAdd'),

    path(
        route = 'DjTraders/Customers/<int:pk>/Edit', 
        view = views.DjTradersCustomerEdit.as_view(), 
        name='DjTraders.CustomerEdit'),

    path(
        route = 'DjTraders/Customers/<int:pk>/Delete', 
        view = views.DjTradersCustomerDelete.as_view(), 
        name='DjTraders.CustomerDelete'),

    path(
        'DjTraders/CustomerDetail/<int:pk>', 
         views.DjTradersCustomerDetailView.as_view(), 
         name='DjTraders.CustomerDetail'),
    
    path(
        'DjTraders/OrdersPlaced',
        views.OrdersPlaced,
        {'selOrderYear': ""},
        name='DjTraders.OrdersPlaced'),

    path(
        'DjTraders/OrdersByDate',
        views.OrdersByDate,
        {'selOrderYear': ""},
        name='DjTraders.OrdersByDate'),

    path(
        'DjTraders/OrdersByCategory',
        views.OrdersByCategory,
        name='DjTraders.OrdersByCategory'),

    path(
        'DjTraders/OrdersByProduct',
        views.OrdersByProduct,
        name='DjTraders.OrdersByProduct'),

    
    
    path(
        'DjTraders/Products', 
         views.DjTradersProductsView.as_view(), 
         name='DjTraders.Products'),
    path(
        'DjTraders/ProductDetail/<int:pk>',
        views.DjTradersProductDetailView.as_view(),
        name='DjTraders.ProductDetail'
    ),
    path(
        route = 'DjTraders/Product/new', 
        view = views.DjTradersProductCreate.as_view(), 
        name='DjTraders.ProductAdd'),
    path(
        route = 'DjTraders/Product/<int:pk>/Edit', 
        view = views.DjTradersProductEdit.as_view(), 
        name='DjTraders.ProductEdit'), 
    path(
        route = 'DjTraders/ProductPurchaseSummary/<int:pk>',
        view = views.DjTradersProductPurchaseSummaryView.as_view(),
        name='DjTraders.ProductPurchaseSummary'),  
    path(
        'DjTraders/TopBottomTenProducts', 
         views.plot_top_bottom_revenue_products, 
        {'selOrderYear': ""},
         name='DjTraders.TopBottomProductOrders'),   
    path(
        route = 'DjTraders/ProductAnalysisPage/<int:pk>',
        view = views.ProductAnalysisPageView.as_view(),
        name='DjTraders.ProductAnalysisPage'),
    path(
        'DjTraders/ProductsMonthlySale',
        views.ProductsMonthlySale,
        {'selOrderYear': ""},
        name='DjTraders.ProductsMonthlySale'),
    path(
        'DjTraders/ProductsSaleAnalysisByCategory',
        views.ProductsSaleAnalysisByCategory,
        name='DjTraders.ProductsSaleAnalysisByCategory'),
    path(
        'DjTraders/ProductSalesAnalysis/<int:pk>',
        views.ProductSalesAnalysis,
        name='DjTraders.ProductSalesAnalysis'),                
 ]