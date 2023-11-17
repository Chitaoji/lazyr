# lazyr
Creates lazily-imported modules in a more readable and safer way.

A lazily-imported module (or a lazy module, to be short) is not physically loaded in the Python environment until its attributes are being accessed. This could be useful when you are importing some modules that are hardly used but take a lot of time to be loaded.

## Installation

```sh
pip install lazyr
```

## How to use
### Make a lazy module
Make *pandas* become a lazy module, for example:

```py
import lazyr
lazyr.register("pandas") # pandas is a lazy module from now on

import pandas as pd
print(pd)
# Output: LazyModule(pandas, ignore=set())

df = pd.DataFrame # pandas is activated and actually loaded now
print(df)
# Output: <class 'pandas.core.frame.DataFrame'>
```

Also, there is a simpler way to create a lazy module, but it may cause *type hints* to lose efficacy:

```py
pd = lazyr.register("pandas")
print(pd)
# Output: LazyModule(pandas, ignore=set())
```

### Wake up a module

The lazy modules are not physically loaded until their attrubutes are imported or used, but sometimes you may want to activate a lazy module without excessing any of its attributes. For that purpose, you can wake up it like this:

```py
lazyr.wakeup(pd) # pandas is no longer lazy now
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 2-Clause License.

## History

### v0.0.3
* Various improvements.

### v0.0.2
* New `lazyr.wakeup` function, for compulsively activating modules.

### v0.0.1
* Initial release.