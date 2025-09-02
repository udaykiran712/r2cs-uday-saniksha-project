{
    'name': 'OWL Training',
    'version': '1.0',
    'summary': 'Basic OWL training example module',
    'category': 'Training',
    'depends': ['base', 'web'],
    'data': [
        # 'views/owl_training_menu.xml',
        # 'views/owl_training_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'owl_training/static/src/components/example/example.js',
            'owl_training/static/src/components/example/example.xml'
        ],
    },
    'installable': True,
    'application': True,
}
