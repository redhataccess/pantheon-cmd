{
    'name': {
        'required': True,
        'type': 'string'
    },
    'path': {
        'required': True,
        'type': ['list', 'string']
    },
    'canonical': {
        'required': True,
        'allowed': [True, False]
    },
    'assemblies': {
        'required': False,
        'type': 'list'
    },
    'modules': {
        'required': False,
        'type': 'list'
    }
}
