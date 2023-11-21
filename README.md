# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the Python environment until its attributes are being accessed. This could be useful when you are importing some modules that are hardly used but take a lot of time to be loaded.

## Installation

```sh
$ pip install lazyr
```

## Usage
### Make a lazy module
Make *pandas* become a lazy module, for example:

```py
>>> import lazyr
>>> lazyr.register("pandas") # pandas is a lazy module from now on
LazyModule(pandas)

>>> import pandas as pd
>>> pd
LazyModule(pandas)

>>> df = pd.DataFrame # pandas is actually loaded now
>>> df
<class 'pandas.core.frame.DataFrame'>
```

There is also a simpler way to create a lazy module, but it may cause *type hints* to lose efficacy:

```py
>>> import lazyr
>>> pd = lazyr.register("pandas")
>>> pd
LazyModule(pandas)
```

### Wake up a module

The lazy modules are not physically loaded until their attrubutes are imported or used, but sometimes you may want to activate a lazy module without accessing any of its attributes. On that purpose, you can 'wake' up the module like this:

```py
>>> lazyr.wakeup(pd) # pandas is woken up and loaded
```

### Ignore attributes

You can make a module even lazier by setting the parameter `ignore`, which ignores the access to certain attributes of the module. The values of the ignored attributes will be set to None, and a lazy module will no longer be activated when its ignored attributes are being accessed.

```py
>>> import lazyr
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"])
LazyModule(pandas, ignore=['DataFrame', 'Series'])

>>> from pandas import DataFrame # pandas is not loaded; DataFrame is set to None
>>> from pandas import Series # pandas is not loaded; Series is set to None
>>> from pandas import io # pandas is loaded because 'io' is not an ignored attribute

>>> from pandas import DataFrame # DataFrame is loaded this time 
>>> DataFrame
<class 'pandas.core.frame.DataFrame'>
```

### Logging

Specify `verbose` when calling `register` to see what exactly will happen to a lazy module during the runtime:

```py
>>> import lazyr
>>> _ = lazyr.register("pandas", verbose=2)
INFO:lazyr:import:pandas

>>> import pandas as pd
DEBUG:lazyr:access:pandas.__spec__

>>> df = pd.DataFrame
DEBUG:lazyr:access:pandas.DataFrame
INFO:lazyr:load:pandas on accessing its attribute 'DataFrame'
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 2-Clause License.

## History

### v0.0.7
* Removed unnecessary objects from the main `lazyr` namespace.

### v0.0.6
* Improved logging:
    * Created a separate logger named 'lazyr' for lazy modules;
    * More detailed logs when `verbose` > 0.

### v0.0.4
* `LazyModule` no longer activated by `_ipython_*` or `_repr_*` methods.

### v0.0.3
* Various improvements.

### v0.0.2
* New function `wakeup`, for compulsively activating modules.

### v0.0.1
* Initial release.