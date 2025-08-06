{
    'name': 'Sale Order Multi Warehouse',
    'version': '17.0',
    'summary': 'Allow selecting warehouse per Sale Order Line and create deliveries grouped by warehouse.',
    'description': """
    This module allows users to manage multiple warehouses at the Sale Order Line level:
    
    ✔ Select a warehouse for each sale order line  
    ✔ Automatically group delivery orders by warehouse upon confirmation  
    ✔ Enhances warehouse-specific logistics visibility and control  
    """,
    'category': 'Sales',
    'sequence': 10,
    'author': 'Namah Softech Private Limited',
    'maintainer': 'Namah Softech Private Limited',
    'company': 'Namah Softech Private Limited',
    'website': 'https://www.namahsoftech.com',
    'support': 'support@namahsoftech.com',
    'price': 19.99,
    'currency': 'USD',
    'contributors': ['Shivani Solanki'],
    'license': 'AGPL-3',
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/img/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
