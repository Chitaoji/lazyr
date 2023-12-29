"""
# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the Python
environment until its attributes are being accessed. This could be useful when you are importing
some modules that are hardly used but take a lot of time to be loaded.

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

The lazy modules are not physically loaded until their attrubutes are imported or used, but
sometimes you may want to activate a lazy module without accessing any of its attributes. On that
purpose, you can 'wake' up the module like this:

```py
>>> lazyr.wakeup(pd) # pandas is woken up and loaded
```

### Ignore attributes

You can make a module even lazier by setting the `ignore` parameter of `register()`, which specifies
the names of attributes to be ignored. The values of the ignored attributes will be set to None, and
a lazy module will no longer be activated by the access to them.

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

Specify the `verbose` parameter when calling `register()` to see what exactly will happen to a lazy
module during the runtime:

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

"""

from .__version__ import __version__
from .core import *
from .core import __all__
