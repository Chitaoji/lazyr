# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the Python environment until its attributes are being accessed. This could be useful when you are importing some modules that are hardly used but take a lot of time to be loaded.


## Installation

```sh
$ pip install lazyr
```

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

There is also a simpler way to create a lazy module, but it may cause *type hints* to lose efficacy:

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

The lazy modules are not physically loaded until their attrubutes are imported or used, but sometimes you may want to activate a lazy module without accessing any of its attributes. On that purpose, you can 'wake up' the module like this:

```py
>>> lazyr.wakeup(scipy) # scipy is woken up and loaded
>>> lazyr.islazy(scipy)
False
```

### Lazy submodules

When registering a lazy module, you may also register some of its submodules by specifying them in the `submodules` parameter of the `register()` function:

```py
>>> lazyr.register("pandas", submodules=["DataFrame", "Series"]) # make DataFrame and Series lazy modules
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
[LazyModule(pandas, submodules=['Series', 'DataFrame']), LazyModule(pandas.DataFrame), LazyModule(pandas.Series)]
```

### Logging

Specify the `verbose` parameter when calling `register()` to see what exactly will happen to a lazy module during the runtime:

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

## History
### v0.1.0
* Requires `python>=3.12` from now on.
* New function `setverbose()` to return a context manager for setting the default verbose value for `register()`.
* Updated `register()`:
    * from now on, parameter `name` will be positional only, and other parameter will be key-word only;
    * parameter `name` can accept multiple module names now;
    * renamed parameter `ignore` to `submodules`.

### v0.0.24
* Updated `register()`: verbosity will be set to the argument `verbose` if lazy module exists.
* Beautified the logging messages.

### v0.0.23
* Updated `register()`: now error will be raised when attempting relative import with no known parent package.

### v0.0.21
* Updated the logging function.

### v0.0.19
* New global variable `VERBOSE`.

### v0.0.18
* Even objects that are not modules can be registered as lazy-modules now, e.g., `pandas.DataFrame`, `numpy.array`, etc.
* The statement `register("foo", ignore=["bar"])` will have the same effect as `register("foo.bar")` now.
* New function `list()`, for checking all the inactivated lazy modules in the system.

### v0.0.17
* Updated README.

### v0.0.16
* New function `islazy()`, for checking the status of a module.
* Improved the representational strings of lazy modules.

### v0.0.15
* Various improvements.

### v0.0.12
* Prettier logs.

### v0.0.11
* Fixed the meta-data.
* Performance enhancements.

### v0.0.9
* Updated LICENSE.

### v0.0.7
* Removed unnecessary objects from the main `lazyr` namespace.

### v0.0.6
* Improved logging:
    * creates a separate logger named 'lazyr' for lazy modules;
    * more detailed logs when `verbose` > 0.

### v0.0.4
* `LazyModule` no longer activated by `_ipython_*()` or `_repr_*()` methods.

### v0.0.3
* Various improvements.

### v0.0.2
* New function `wakeup()`, for compulsively activating modules.

### v0.0.1
* Initial release.