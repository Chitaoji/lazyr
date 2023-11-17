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

The lazy modules are not physically loaded until their attrubutes are imported or used, but sometimes you may want to activate a lazy module without excessing any of its attributes. On that purpose, you can 'wake' up the module like this:

```py
>>> lazyr.wakeup(pd) # pandas is woken up and loaded
```

### Ignore attributes

You can make a lazy module even lazier by ignoring certain attributes when regestering it. The `ignore` parameter of `lazyr.register` specifies the ignored attrbutes. When an ignored attribute is accessed, the lazy module will still remain unloaded.

```py
>>> import lazyr
>>> pd = lazyr.register("pandas", ignore=["DataFrame", "Series"])
>>> from pandas import DataFrame # pandas is still lazy
>>> from pandas import Series # pandas is still lazy
>>> from pandas import io # pandas is loaded because 'io' is not an ignored attribute
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 2-Clause License.

## History

### v0.0.4
* `LazyModule` no longer activated by `_ipython_*` or `_repr_*` methods.

### v0.0.3
* Various improvements.

### v0.0.2
* New `lazyr.wakeup` function, for compulsively activating modules.

### v0.0.1
* Initial release.