# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the Python environment until its attributes are being accessed. This could be useful when you are importing some modules that are hardly used but take a lot of time to be loaded.

## README.md

* en [English](README.md)
* zh_CN [简体中文](README.zh_CN.md)

## Installation

```sh
$ pip install lazyr
```

## Usage
### Make a lazy module
Make *pandas* become a lazy module, for example:

```py
>>> import lazyr
>>> lazyr.register("pandas") # pandas becomes a lazy module
LazyModule(pandas) # this is the LazyModule object corresponding to pandas

>>> import pandas as pd # pandas is not loaded since it's lazy
>>> pd
LazyModule(pandas) # pd is assigned the LazyModule object corresponding to pandas

>>> df = pd.DataFrame # pandas is actually loaded now
>>> pd
<module 'pandas' from '/../..'>
```

There is also a simpler way to create a lazy module, but it may cause *type hints* to lose efficacy:

```py
>>> import lazyr
>>> pd = lazyr.register("pandas")
>>> pd
LazyModule(pandas)
```

### Check if a module is lazy

Use `islazy()` to check if a module is lazy or not:

```py
>>> lazyr.islazy(pd)
True
```

### Wake up a module

The lazy modules are not physically loaded until their attrubutes are imported or used, but sometimes you may want to activate a lazy module without accessing any of its attributes. On that purpose, you can 'wake' up the module like this:

```py
>>> lazyr.wakeup(pd) # pandas is woken up and loaded
>>> lazyr.islazy(pd)
False
```

### Ignore attributes

You can make a module even lazier by setting the `ignore` parameter of `register()`, which specifies the names of attributes to be ignored. The values of the ignored attributes will be set to None, and a lazy module will no longer be activated by the access to them.

```py
>>> import lazyr
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"]) # Ignoring DataFrame and Series
LazyModule(pandas, ignore=['DataFrame', 'Series'])

>>> from pandas import DataFrame # pandas is not loaded; DataFrame is set to None
>>> from pandas import Series # pandas is not loaded; Series is set to None
>>> from pandas import io # pandas is loaded because 'io' is not an ignored attribute

>>> from pandas import DataFrame # DataFrame is loaded this time 
>>> DataFrame
<class 'pandas.core.frame.DataFrame'>
```

### Logging

Specify the `verbose` parameter when calling `register()` to see what exactly will happen to a lazy module during the runtime:

```py
>>> import lazyr
>>> _ = lazyr.register("pandas", verbose=2)
INFO:lazyr:import:pandas

>>> import pandas as pd
DEBUG:lazyr:access:pandas.__spec__

>>> df = pd.DataFrame
DEBUG:lazyr:access:pandas.DataFrame
INFO:lazyr:load:pandas(.DataFrame)
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 3-Clause License.

## History

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
    * Created a separate logger named 'lazyr' for lazy modules;
    * More detailed logs when `verbose` > 0.

### v0.0.4
* `LazyModule` no longer activated by `_ipython_*()` or `_repr_*()` methods.

### v0.0.3
* Various improvements.

### v0.0.2
* New function `wakeup()`, for compulsively activating modules.

### v0.0.1
* Initial release.