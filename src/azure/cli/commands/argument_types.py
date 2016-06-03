from collections import defaultdict

# pylint: disable=too-many-arguments,too-few-public-methods
class CliArgumentType(object):

    def __init__(self, options_list=None, base_type=str, overrides=None, completer=None,
                 validator=None, **kwargs):
        self.options_list = ()
        self.completer = completer
        self.validator = validator
        if overrides:
            self.options_list = overrides.options_list
            self.options = overrides.options.copy()
            self.base_type = overrides.base_type
        else:
            self.options = {}

        self.base_type = base_type
        self.update(options_list=options_list, **kwargs)

    def update(self, options_list=None, completer=None, validator=None, **kwargs):
        self.options_list = options_list or self.options_list
        self.completer = completer or self.completer
        self.validator = validator or self.validator
        self.options.update(**kwargs)

class CliCommandArgument(CliArgumentType):
    def __init__(self, dest, options_list=None, completer=None, validator=None, **kwargs):
        if not options_list:
            options_list = '--' + dest.replace('_', '-')

        super(CliCommandArgument, self).__init__(**kwargs)
        self.update(options_list=options_list, completer=completer, validator=validator, **kwargs)
        self.options['dest'] = dest

    def name(self):
        return self.options['dest']

class _ArgumentRegistry(object):

    def __init__(self):
        self.arguments = defaultdict(lambda: {})

    def register_cli_argument(self, scope, dest, argtype, options_list, **kwargs):
        argument = CliArgumentType(options_list=options_list, overrides=argtype,
                                   completer=argtype.completer, validator=argtype.validator,
                                   **kwargs)
        self.arguments[scope][dest] = argument

    def get_cli_argument(self, command, name):
        parts = command.split()
        result = CliArgumentType()
        for index in range(0, len(parts) + 1):
            probe = ' '.join(parts[0:index])
            override = self.arguments.get(probe, {}).get(name, None)
            if override:
                result.update(override.options_list,
                              completer=override.completer,
                              validator=override.validator,
                              **override.options)
        return result

def register_cli_argument(scope, dest, argtype, options_list=None, **kwargs):
    '''Specify CLI specific metadata for a given argument for a given scope.
    '''
    _cli_argument_registry.register_cli_argument(scope, dest, argtype, options_list, **kwargs)

def register_extra_cli_argument(command, dest, options_list=None, **kwargs):
    '''Register extra parameters for the given command. Typically used to augment auto-command built
    commands to add more parameters than the specific SDK method introspected.
    '''
    _cli_extra_argument_registry[command][dest] = CliCommandArgument(dest, options_list, **kwargs)

def get_cli_argument(command, argname):
    return _cli_argument_registry.get_cli_argument(command, argname)

def get_cli_extra_arguments(command):
    return _cli_extra_argument_registry[command].items()

_cli_argument_registry = _ArgumentRegistry()
_cli_extra_argument_registry = defaultdict(lambda: {})