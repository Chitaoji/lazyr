"""
Contains the core of lazyr: register(), wakeup(), etc.

NOTE: this module is private. All functions and objects are available in the main
`lazyr` namespace - use that instead.

"""
import importlib
import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Set, Union

if TYPE_CHECKING:
    from types import ModuleType

__all__ = ["register", "wakeup", "isawake"]


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
        Specifies the names of attributes to be ignored. The values of the ignored
        attributes will be set to None, and a lazy module will no longer be activated
        by the access to them.
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
        getattr(m, "_LazyModule__ignore")(ignore)
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
        getattr(module, "_LazyModule__wakeup")()


def isawake(module: Union["ModuleType", str]) -> bool:
    """
    Checks if a module is a functional one (including real modules and lazy
    modules that have been activated) or not.

    Parameters
    ----------
    module : Union[&quot;ModuleType&quot;, str]
        Can be either a `ModuleType` object or a string representing the name of a
        module.

    Returns
    -------
    bool
        Whether the module is functional.

    Raises
    ------
    ModuleNotFoundError
        Raised when the module is not found.

    """
    if isinstance(module, str):
        if module not in sys.modules:
            raise ModuleNotFoundError(f"no module named '{module}'")
        module = sys.modules[module]
    if isinstance(module, LazyModule):
        return bool(getattr(module, "_LazyModule__module"))
    return True


class LazyModule:
    """
    An implementation of a lazy module.

    Note that this should NEVER be instantiated directly, but always through the module-level
    function `lazyr.register()`.

    """

    __skipped_attrs = {"__spec__", "__path__"}
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
        self.__logger = self.__logger_init()

        if p := self.__get_parent():
            register(p, ignore=[self.__get_suffix()], verbose=verbose)

    def __repr__(self):
        if self.__ignored_attrs:
            ignore_repr = f", ignore={list(self.__ignored_attrs)}"
        else:
            ignore_repr = ""
        return f"{self.__class__.__name__}({self.__name}{ignore_repr})"

    def __getattr__(self, __name: str) -> Any:
        self.__access_logging(__name)
        if not self.__module:
            if __name in self.__skipped_attrs:
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
            self.__wakeup_logging("__wakeup" if __name is None else __name)

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

    def __logger_init(self) -> Optional["logging.Logger"]:
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

    def __access_logging(self, __name: str) -> None:
        if self.__verbose >= 2:
            self.__logger.debug(
                "access:%s.%s%s", self.__name, __name, self.__get_frame_info(3)
            )

    def __wakeup_logging(self, __name: str) -> None:
        if self.__verbose >= 1:
            self.__logger.info(
                "activate:%s(.%s)%s",
                self.__name,
                __name,
                self.__get_frame_info(4),
            )

    def __get_frame_info(self, depth: int) -> str:
        if self.__verbose < 3:
            return ""
        f = inspect.stack()[depth]
        return f" ----> {f[1]} --> {f[3]} --> {f[4][0].strip() if isinstance(f[4], list) else None}"

    def __get_family(self) -> List[str]:
        names: List[str] = [tmp := (splits := self.__name.split("."))[0]]
        for i in splits[1:]:
            names.append(tmp := f"{tmp}.{i}")
        return names

    def __get_parent(self) -> str:
        return self.__name.rpartition(".")[0]

    def __get_suffix(self) -> str:
        return self.__name.rpartition(".")[-1]
