"""
# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the
Python environment until its attributes are being accessed. This could be useful when
you are importing some modules that are hardly used but take a lot of time to be loaded.

## README.md

* en [English](README.md)
* zh_CN [Simplified Chinese](README.zh_CN.md)

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

### Ignore attributes

You can make a module even lazier by setting the `ignore` parameter of `register()`,
which specifies the names of submodules to be ignored. The ignored submodules will
become lazy modules, too.

```py
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"]) # make DataFrame and Series
lazy modules
LazyModule(pandas, ignore=['DataFrame', 'Series'])
```

The statement above has roughly the same effect as the following code piece:

```py
>>> _, _ = lazyr.register("pandas.DataFrame"), lazyr.register("pandas.Series")
```

### List all lazy modules

Use `listall()` to check all the inactivated lazy modules in the system:

```py
>>> lazyr.listall()
[LazyModule(pandas, ignore=['Series', 'DataFrame']), LazyModule(pandas.DataFrame),
LazyModule(pandas.Series)]
```

### Logging

Specify the `verbose` parameter when calling `register()` to see what exactly will
happen to a lazy module during the runtime:

```py
>>> _ = lazyr.register("matplotlib.pyplot", verbose=2)
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

from .__version__ import __version__
from .core import *
from .core import __all__
