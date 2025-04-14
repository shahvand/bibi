# Inventory Workflow Management System

This is a Django-based inventory workflow management system designed to handle order requests, approvals, delivery tracking, and reporting for inventory management across multiple branches.

## Features

- User role-based access control (Requester, Warehouse Manager, Accountant, Admin)
- Order workflow management (requesting, approving, delivering, receiving)
- Product management
- Driver management
- Order tracking and reporting
- Invoice generation

## System Requirements

- Python 3.8+
- MySQL database
- Django 5.2+

## Installation and Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory-management
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your database settings:
```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
```

5. Run migrations:
```bash
python manage.py makemigrations workflow
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## User Types and Permissions

- **Requester**: Branch representatives who can place orders and confirm receipt of goods
- **Warehouse Manager**: Users who approve/reject orders, adjust quantities, set prices, and manage products and drivers
- **Accountant**: Users who have read-only access to orders and can generate reports
- **Admin**: Superusers who have full system access

## Workflow Process

1. **Order Request**:
   - Requester fills out an order form specifying products, quantities, etc.
   - Order is saved with 'PENDING' status

2. **Order Approval**:
   - Warehouse Manager reviews pending orders
   - Manager can adjust quantities, set prices, add notes
   - Order is either approved or rejected

3. **Order Delivery**:
   - Warehouse Manager marks the order as delivered
   - Driver is assigned for delivery
   - Order status changes to 'DELIVERED'

4. **Order Receipt**:
   - Requester confirms receipt of goods
   - Order status changes to 'RECEIVED'

5. **Reporting**:
   - Accountants can generate various reports on orders, products, etc.
   - Invoice generation is available for completed orders

## Project Structure

- `workflow/models.py`: Database models
- `workflow/views.py`: View functions and classes
- `workflow/forms.py`: Form classes
- `workflow/urls.py`: URL routing
- `templates/workflow/`: HTML templates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

[Your Name/Organization] 