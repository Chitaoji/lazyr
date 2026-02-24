"""
# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the
Python environment until its attributes are being accessed. This could be useful when
you are importing some modules that are hardly used but take a lot of time to be loaded.


## Usage
### Make a lazy module
Make *numpy* become a lazy module, for example:

```py
>>> import lazyr
>>> lazyr.register("numpy") # numpy becomes a lazy module
LazyModule(numpy) # this is the LazyModule object

>>> import numpy as np # numpy is not loaded since it's lazy
>>> np
LazyModule(numpy) # np is assigned the LazyModule object instead

>>> arr = np.array([]) # numpy is actually loaded now
>>> np
<module 'numpy' from '/../..'>
```

There is also a simpler way to create a lazy module, but it may cause *type hints* to
lose efficacy:

```py
>>> np = lazyr.register("numpy")
```

When registering multiple modules, you can specify more than one names:

```py
>>> lazyr.register("pandas", "scipy")
[LazyModule(pandas), LazyModule(scipy)]
```

### Check if a module is lazy

Use `islazy()` to check if a module is lazy or not:

```py
>>> scipy = lazyr.register("scipy")
>>> lazyr.islazy(scipy)
True
```

### Wake up a module

The lazy modules are not physically loaded until their attrubutes are imported or used,
but sometimes you may want to activate a lazy module without accessing any of its
attributes. On that purpose, you can 'wake up' the module like this:

```py
>>> lazyr.wakeup(scipy) # scipy is woken up and loaded
>>> lazyr.islazy(scipy)
False
```

### Lazy submodules

When registering a lazy module, you may also register some of its submodules by
specifying them in the `submodules` parameter of the `register()` function:

```py
>>> lazyr.register("pandas", submodules=["DataFrame", "Series"]) # make DataFrame and
Series lazy modules
LazyModule(pandas, submodules=['DataFrame', 'Series'])
```

The statement above has roughly the same effect as the following code piece:

```py
>>> lazyr.register("pandas.DataFrame", "pandas.Series")
[LazyModule(pandas.DataFrame), LazyModule(pandas.Series)]
```

### List all lazy modules

Use `listall()` to check all the inactivated lazy modules in the system:

```py
>>> lazyr.listall()
[LazyModule(pandas, submodules=['Series', 'DataFrame']), LazyModule(pandas.DataFrame),
LazyModule(pandas.Series)]
```

### Logging

Specify the `verbose` parameter when calling `register()` to see what exactly will
happen to a lazy module during the runtime:

```py
>>> with lazyr.setverbose(2):
...     _ = lazyr.register("matplotlib.pyplot")
...
INFO:lazyr:register -> matplotlib.pyplot
INFO:lazyr:register -> matplotlib

>>> import matplotlib.pyplot as plt
DEBUG:lazyr:access -> matplotlib.pyplot.__spec__
DEBUG:lazyr:access -> matplotlib.__spec__
DEBUG:lazyr:access -> matplotlib.pyplot

>>> plot = plt.plot
DEBUG:lazyr:access -> matplotlib.pyplot.plot
INFO:lazyr:load -> matplotlib.pyplot(.plot)
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 3-Clause License.

"""

from ._version import __version__
from .core import *
from .core import __all__
