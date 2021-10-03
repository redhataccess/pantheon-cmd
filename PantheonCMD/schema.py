{
    'server': {
        'required': True,
        'type': 'string'
    },
    'repository': {
        'required': True,
        'type': 'string'
    },
    'variants': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'required': True,
                    'type': 'string'
                },
                'path': {
                    'required': True,
                    'type': ['string', 'list']
                },
                'canonical': {
                    'required': True,
                    'allowed': [True, False]
                }
            }
        }
    },
    'assemblies': {
        'required': True,
        'type': 'list'
    },
    'modules': {
        'required': True,
        'type': 'list'
    },
    'resources': {
        'required': True,
        'type': 'list'
    }
}
