# Application Design and Development using Python and Django

**Application Name - Django Traders** It is a Python and Django-based application designed to manage customers and products with the following functionality:


**Home Page:** which provides a home landing point to navigate the site, and its apps from.

**Manage Customers and their Orders Page:**

  - **Customer Search and Display:** The customers data should support flexible searching and sorting of all displayed information. 

  - **Customers Details View:** Enhance the Search and Display of the customer detail view to display information about a specific customer. This view should show
  information about the customer - name, contact, address, etc. and well as information about the orders that the customers have placed. 

  - **Create and Update:** Allow the user to perform Create and Update operations on the customers of DJTraders customers. 

**Manage Products Page:**
  
  - **Product Search and Display:** Implement Searches for products using Name, Price (greater or less than search) and Category. Any changes in the selection or a text change should trigger the search and display the results.

  - **Products Details View:** Enhance the display of the products detail view to display information customers who have bought this product. This view should show a link                 to the details view of the customer who has bought the product. 

  - **Create and Update:** Allow the user to perform Create and Update operations.

# Technologies Used

  -  Python 3.x
  -  Django
  -  SQLite (or any other database

# Installation in Visual Studio Code Prerequisites Before proceeding, make sure to installed the following :

  - Python (version 3.x): Download Python from https://www.python.org/downloads/
  - Django: This will be installed as part of the setup
  - Visual Studio Code: Download VS Code from https://code.visualstudio.com/
  - VS Code Extensions: Python extension for VS Code

# Step-by-Step Guide

  1. Open the project folder 'DjangoTraders' in Visual Studio Code and Navigate into the project directory. (cd DjangoTraders)
  2. Set up a Python virtual environment. (python3 -m venv venv)
  3. Install the dependencies: (pip install -r requirements.txt)
  4. Install VS Code extensions.
  5. Run migrations: (python manage.py migrate)
  6. Run the application: (python manage.py runserver)
  7. Open a browser and navigate to http://127.0.0.1:8000/ to view the application.

