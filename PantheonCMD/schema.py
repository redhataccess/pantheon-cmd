{
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
                'attributes': {
                    'required': True,
                    'type': 'list'
                },
                'nav': {
                    'required': False,
                    'type': 'string'
                },
                'build': {
                    'required': True,
                    'allowed': [True, False]
                },
                'files': {
                    'required': True,
                    'type': 'dict',
                    'schema': {
                        'included': {
                            'required': True,
                            'type': 'list'
                        },
                        'excluded': {
                            'required': False,
                            'type': 'list'
                        }
                    }
                }
            }
        }
    }
}
