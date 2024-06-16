import types
import inspect
import numpy as np
from pathlib import Path


modules = [
    #'',
    'np.exceptions',
    'np.fft',
    'np.linalg',
    'np.polynomial',
    'np.polynomial.chebyshev',
    'np.polynomial.hermite',
    'np.polynomial.hermite_e',
    'np.polynomial.laguerre',
    'np.polynomial.legendre',
    'np.polynomial.polynomial',
    'np.random',
    'np.strings',
    #'testing',
    'np.typing',
    # Special - Purpose
    'np.ctypeslib',
    'np.dtypes',
    'np.emath',
    'np.lib',
    'np.lib.format',
    'np.lib.mixins',
    # 'lib.recfunctions', #Not visible
    'np.lib.scimath',
    'np.lib.stride_tricks',
    'np.lib.npyio',
    'np.lib.introspect',
    'np.lib.array_utils',
    'np.rec',
    'np.version',
    # legacy
    'np.char', #Use strings instead
    #'distutils', #deprecated
    'np.f2py', # legacy
    'np.ma', # not reliable
    #'np.ma.extras', #imported with 'np.ma'. Skip.
    #'ma.mrecords', # Still experimental
    #'matlib', # pending deprecation # Functions are available in main namespace and not documented online.
    #'np.matrixlib', # imported with 'np'. Skip.
    'np',
]


skip = [
    # Three of these functions appear in conf.py as coverage_ignore_functions. I'm guessing I have the same issue.
    #'np.ma.alltrue', #Type issue
    #'np.ma.sometrue', #Type issue
    #'np.bitwise_not', #Ufunct loop may be off
    ##################### HELP NEEDED:  I'd prefer to use a different method to check deprecation.
    ### Option in refguide_check. Probably move this whole file there, with new --linked_rst option.
    #'np.row_stack', #is deprecated alias. The check below misses the alias.
    #'np.abs', # Another ufunct loop may be off
    ]

def main(search_version=1):

    print('Listing all functions in each module and saving them as log files')
    print(f'NumPy version: {np.__version__}')

    # Dyanamically get 'np._ArrayFunctionDispatcher' as a type to check for.
    # as well as a few others that get missed.
    dispatcher_type = type(getattr(eval('np.linalg'),'matrix_power'))
    random_type = type(getattr(eval('np.random'),'rand'))
    default_rng_type = type(getattr(eval('np.random'),'default_rng'))
    ufunc_type = type(getattr(eval('np.strings'),'not_equal'))

    # Define the log directory and ensure it exists
    log_dir = Path("log")
    log_dir.mkdir(parents=True, exist_ok=True)

    with open(log_dir / 'module_list.log', 'w') as module_log_file:
        for module_name in modules:
            log_file = module_name.replace('.', '_') + '.log'
            mod = eval(module_name)

            #We want callable functions.
            objects = [(name, getattr(mod, name))
                            for name in getattr(mod, '__all__', dir(mod))
                                if not name.startswith('_')]

            # for item in objects: print(item)
            # print(f'Objects: {len(objects)}')

            if search_version == 1:
                # This section requires import types
                funcs = [item for item in objects
                            if isinstance(item[1], (types.FunctionType,
                                                    types.BuiltinFunctionType,
                                                    types.MethodDescriptorType,
                                                    np.ufunc,
                                                    dispatcher_type,
                                                    random_type,
                                                    default_rng_type,
                                                    ufunc_type,
                                                    ))]
            else:
                # This version is quicker, but catches ma.alltrue and ma.sometrue
                # This version misses ufunc types
                funcs = [item for item in objects
                            if inspect.isroutine(item[1])]

            # Enable this to test all items
            # funcs = objects

            # Ignore functions that are explicitly deprecated.
            # Checking for the words "is deprecated" is a terrible idea
            # The function linalg.qr has these words in it, but it's not deprecated.
            non_deprecated = [item for item in funcs
                        if ("is deprecated" not in item[1].__doc__)]
            # non_deprecated = funcs
            searchfuncs = [item[0] for item in non_deprecated]
            # Remove skipped items
            searchfuncs = [item for item in searchfuncs
                        if ((module_name + '.' + item) not in skip)]

            if len(searchfuncs) > 0:
                searchfuncs = sorted(searchfuncs)

                with open(log_dir / log_file, 'w') as log:
                    for item in searchfuncs:
                        log.write(item + '\n')
                module_log_file.write(module_name + '\n')

if __name__ == '__main__':
    main(search_version=1)