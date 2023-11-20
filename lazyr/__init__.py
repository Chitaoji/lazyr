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
sometimes you may want to activate a lazy module without excessing any of its attributes. On that
purpose, you can 'wake' up the module like this:

```py
>>> lazyr.wakeup(pd) # pandas is woken up and loaded
```

### Ignore attributes

You can make a lazy module even lazier by ignoring certain attributes when regestering it. The 
`ignore` parameter of `lazyr.register` specifies the ignored attrbutes. When an ignored attribute 
is accessed, the lazy module will still remain unloaded.

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

"""
import importlib
import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Set

from .__version__ import __version__

if TYPE_CHECKING:
    from types import ModuleType

__all__ = ["register", "wakeup"]


def register(
    name: str,
    package: Optional[str] = None,
    ignore: Optional[List[str]] = None,
    verbose: Literal[0, 1, 2, 3] = 0,
) -> "ModuleType":
    """
    Register a module as a lazy one. A lazy module is not physically loaded in the
    Python environment until its attributes are being accessed, or compulsively
    activated by the user.

    Parameters
    ----------
    name : str
        Name of the module to be registerd.
    package : Optional[str], optional
        Required when performing a relative import. It specifies the package to use
        as the anchor point from which to resolve the relative import to an absolute
        import, by default None.
    ignore : Optional[List[str]], optional
        Specifies the ignored attributes of the lazy module. A lazy module will not
        be activated on accessing to an ignored attribute, and the attribute itsef
        will be set to None.
    verbose : Literal[0, 1, 2, 3], optional
        Specifies the level of verbosity for logging. It accepts values from 0 to 3,
        where:
            0 : disables logging;
            1 : logs the importing and loading of lazy modules with level INFO;
            2 : also logs the accessing of lazy modules' attributes with level DEBUG;
            3 : adds stack infomation, NOTE: this will SLOW down the program.
        By default 0.

    Returns
    -------
    ModuleType
        The lazy module.

    Raises
    ------
    TypeError
        Raised if not a relative import when the `package` argument is provided.

    """
    if (module_name := __join_module_name(name, package=package)) not in sys.modules:
        sys.modules[module_name] = LazyModule(
            module_name, ignore=ignore, verbose=verbose
        )
    elif isinstance(m := sys.modules[module_name], LazyModule):
        getattr(m, "!ignore")(ignore)
    return sys.modules[module_name]


def __join_module_name(name: str, package: Optional[str] = None):
    if package is None:
        return name
    if not name.startswith("."):
        raise TypeError(
            f"expected a relative import when the `package` argument is provided, \
got '{name}' instead"
        )
    return package + name


def wakeup(module: "ModuleType"):
    """
    Compulsively activates a lazy module by loading it as a normal one.

    Parameters
    ----------
    module : ModuleType
        The module to be activated.

    """
    if isinstance(module, LazyModule):
        getattr(module, "!wakeup")()


class LazyModule:
    """
    A lazy module.

    """

    __skipped: Set = {"__spec__", "__path__"}
    __skipped_startswith = ("_ipython_", "_repr_")

    def __init__(
        self,
        name: str,
        ignore: Optional[List[str]] = None,
        verbose: Literal[0, 1, 2, 3] = 0,
    ) -> None:
        self.__name = name
        self.__ignored_attrs: Set[str] = set()
        self.__ignore(ignore)
        self.__verbose = verbose
        self.__module: Optional[ModuleType] = None
        self.__logger = self.__logging_import()

        if p := self.__get_parent():
            register(p, ignore=[self.__get_suffix()], verbose=verbose)

    def __repr__(self):
        if self.__ignored_attrs:
            ignore_repr = f", ignore={list(self.__ignored_attrs)}"
        else:
            ignore_repr = ""
        return f"{self.__class__.__name__}({self.__name}{ignore_repr})"

    def __getattr__(self, __name: str) -> Any:
        if __name.startswith("!"):
            return getattr(self, f"_{self.__class__.__name__}__{__name[1:]}")
        self.__logging_access(__name)
        if self.__module is None:
            if __name in self.__skipped:
                if not sys._getframe(1).f_code.co_name == "_find_and_load_unlocked":
                    return None
            elif __name.startswith(self.__skipped_startswith):
                return None
            elif __name in self.__ignored_attrs:
                if (module_name := f"{self.__name}.{__name}") in sys.modules:
                    return sys.modules[module_name]
                return None
            self.__wakeup(__name)
        return getattr(self.__module, __name)

    def __wakeup(self, __name: Optional[str] = None) -> None:
        if self.__import_module():
            self.__logging_load("__wakeup" if __name is None else __name)

    def __ignore(self, ignore: Optional[List[str]] = None) -> None:
        if ignore is not None:
            self.__ignored_attrs |= set(ignore)

    def __import_module(self) -> bool:
        res: bool = False
        for name in self.__get_family():
            if isinstance(m := sys.modules[name], self.__class__):
                del sys.modules[name]
                module = importlib.import_module(name)
                if name == self.__name:
                    res = True
            else:
                module = m
        self.__module = module
        return res

    def __logging_import(self) -> Optional["logging.Logger"]:
        if self.__verbose >= 1:
            logger = logging.getLogger("lazyr")
            logger.propagate = False
            if not logger.hasHandlers():
                logger.setLevel(logging.DEBUG)
                sh = logging.StreamHandler()
                fm = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
                sh.setFormatter(fm)
                logger.addHandler(sh)
            logger.info("import:%s", self.__name)
            return logger
        return None

    def __logging_access(self, __name: str) -> None:
        if self.__verbose >= 2:
            self.__logger.debug(
                "access:%s.%s%s", self.__name, __name, self.__get_frame_info(3)
            )

    def __logging_load(self, __name: str) -> None:
        if self.__verbose >= 1:
            self.__logger.info(
                "load:%s on accessing to its attribute '%s'%s",
                self.__name,
                __name,
                self.__get_frame_info(4),
            )

    def __get_frame_info(self, depth: int) -> str:
        if self.__verbose < 3:
            return ""
        f = inspect.stack()[depth]
        return f" by {f[1]} - {f[3]} - {f[4][0].strip() if isinstance(f[4], list) else None}"

    def __get_family(self) -> List[str]:
        names: List[str] = []
        return [".".join(names := names + [i]) for i in self.__name.split(".")]

    def __get_parent(self) -> str:
        return self.__name.rpartition(".")[0]

    def __get_suffix(self) -> str:
        return self.__name.rpartition(".")[-1]
