# lazyr
Creates lazy modules in a more readable and safer way.

## Installation

```sh
pip install lazyr
```

## Usage
Let *pandas* be a lazy module, for example:

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

There is also a simpler way to create a lazy module, but may cause *type hints* to lose efficacy:

```py
import lazyr
pd = lazyr.register("pandas") # pandas is a lazy module from now on
print(pd)
# Output: LazyModule(pandas, ignore=set())
```

### Wake up a module

Sometimes you may want to activate a lazy module without excessing any of its attributes, you can wake up it like this:

```py
lazyr.wakeup(pd) # pandas is no longer lazy
```

### Safe space

Remember that leaving a lazy module inactivated *forever* may be **very** dangerous, for example, the following codes will cause an error:

```py
lazyr.register("pandas")

from pandas.io.formats.style import Styler # Oops, submodules of submodules of a lazy module are not accessable
# ModuleNotFoundError: No module named 'pandas.io.formats'; 'pandas.io' is not a package
```

Compared to:

```py
lazyr.register("pandas")

from pandas import io # This is ok, and pandas will be loaded
```

This is because the lazy modules tried to be as 'lazy' as possible, and overrided their submodules. One way to fix this is by using `wakeup()`:

```py
pd = lazyr.register("pandas")
lazyr.wakeup(pd)
from pandas.io.formats.style import Styler # Fine now
```

But this may be very boring, since you may need to wake up every unused lazy module at the end of your own python file (in order not to cause problems for others who import your file).

A more beautiful way is to use `sefe()`:

```py
with lazyr.safe():
    # Create and import lazy modules inside the 'safe' space
    lazyr.register("pandas")

# Modules are less 'lazy' outside the 'safe' space 
from pandas.io.formats.style import Styler # Fine now
```

## See Also
### Github repository
* https://github.com/Chitaoji/lazyr/

### PyPI project
* https://pypi.org/project/lazyr/

## License
This project falls under the BSD 2-Clause License.

## History

### v0.0.2
* Added new features `lazyr.wakeup` and `lazyr.safe`.

### v0.0.1
* Initial release.