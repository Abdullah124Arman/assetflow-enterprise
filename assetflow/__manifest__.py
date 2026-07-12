{
    'name': 'AssetFlow',
    'version': '1.0',
    'category': 'Operations/Asset Management',
    'summary': 'Enterprise Asset & Resource Management System',
    'description': """
AssetFlow
=========
A centralized ERP platform for tracking, allocating, and maintaining physical assets and shared resources.
Designed for a clean, role-based architecture without relying on accounting or purchasing.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/asset_sequence.xml',
        'views/menu_views.xml',
        'views/department_views.xml',
        'views/employee_views.xml',
        'views/category_views.xml',
        'views/asset_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
