"""The design extra package.

Notes
-----
    To us the extras module you have to import it manually by calling:
    `import expyriment.design.extras`


"""

__author__ = 'Florian Krause <florian@expyriment.org> \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = ''
__revision__ = ''
__date__ = ''


import os as _os

import defaults
from expyriment import _importer_functions


for _plugins in [_importer_functions.import_plugins(__file__),
                _importer_functions.import_plugins_from_settings_folder(__file__)]:
    for _plugin in _plugins:
        try:
            exec(_plugins[_plugin])
        except:
            print("Warning: Could not import {0}".format(
                _os.path.dirname(__file__) + _os.sep + _plugin))
