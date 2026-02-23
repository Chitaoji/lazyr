"""
Contains the core of lazyr: register(), wakeup(), etc.

NOTE: this module is private. All functions and objects are available in the main
`lazyr` namespace - use that instead.

"""

import importlib
import logging
import sys
import traceback
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Set, Union

if TYPE_CHECKING:
    from types import ModuleType

__all__ = ["register", "wakeup", "islazy", "listall", "LazyModule", "VERBOSE"]

VERBOSE = 0


def register(
    name: str,
    package: Optional[str] = None,
    ignore: Optional[List[str]] = None,
    verbose: Optional[Literal[0, 1, 2, 3]] = None,
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
        Specifies the names of attributes to be ignored. The ignored attributes will be
        set to lazy modules, too.
    verbose : Literal[0, 1, 2, 3], optional
        Specifies the level of verbosity for logging. It accepts values from 0 to 3,
        where:
            0 : disables logging;
            1 : logs the importing and loading of lazy modules with level INFO;
            2 : also logs the accessing of lazy modules' attributes with level DEBUG;
            3 : adds stack infomation, NOTE: this will SLOW down the program.
        By default `VERBOSE`.

    Returns
    -------
    ModuleType
        The lazy module.

    Raises
    ------
    TypeError
        Raised if an absolute import when the `package` argument is provided, or if a
        relative import without the `package` argument.

    """
    if verbose is None:
        verbose = getattr(sys.modules[__name__.rpartition(".")[0]], "VERBOSE")
    if (module_name := __join_module_name(name, package=package)) not in sys.modules:
        sys.modules[module_name] = LazyModule(
            module_name, ignore=ignore, verbose=verbose
        )
    elif isinstance(m := sys.modules[module_name], LazyModule):
        getattr(m, "_LazyModule__ignore")(ignore)
        getattr(m, "_LazyModule__set_verbose")(verbose)
    return sys.modules[module_name]


def __join_module_name(name: str, package: Optional[str] = None) -> None:
    if name.startswith("."):
        if package is None:
            frame = sys._getframe(2)  # pylint: disable=protected-access
            if (package := frame.f_globals["__name__"]) == "__main__":
                raise TypeError(
                    "attempted relative import with no known parent package"
                )
        return package + name
    if package is None:
        return name
    raise TypeError(
        "expected a relative import when the 'package' argument is provided"
    )


def wakeup(module: "ModuleType") -> None:
    """
    Compulsively activates a lazy module by loading it as a normal one.

    Parameters
    ----------
    module : ModuleType
        The module to be activated.

    """
    if isinstance(module, LazyModule):
        getattr(module, "_LazyModule__wakeup")()


def islazy(module: Union["ModuleType", str]) -> bool:
    """
    Checks if a module is lazy or not. Returns False if received a `LazyModule`
    object that has not been activated yet, otherwise returns True. If only to
    check the type of the module, please try `isinstance()`.

    Parameters
    ----------
    module : Union[ModuleType, str]
        Can be either a `ModuleType` object or a string representing the name of
        a module.

    Returns
    -------
    bool
        If the module is lazy or not.

    Raises
    ------
    ModuleNotFoundError
        Raised when the module is not found.

    """
    if isinstance(module, str):
        if module not in sys.modules:
            raise ModuleNotFoundError(f"no module named {module!r}")
        module = sys.modules[module]
    if isinstance(module, LazyModule):
        return not bool(getattr(module, "_LazyModule__module"))
    return False


def listall() -> List["LazyModule"]:
    """
    List all the inactivated lazy modules.

    Returns
    -------
    List[LazyModule]
        List of lazy modules.

    """
    module_list: List["LazyModule"] = []
    for m in sys.modules.values():
        if isinstance(m, LazyModule) and not bool(getattr(m, "_LazyModule__module")):
            module_list.append(m)
    return module_list


class LazyModule:
    """
    An implementation of a lazy module.

    Note that this should NEVER be instantiated directly, but always through the
    module-level function `lazyr.register()`.

    """

    __skipped_attrs = {"__spec__", "__path__"}
    __skipped_startswith = ("_ipython_", "_repr_")

    def __init__(
        self,
        name: str,
        ignore: Optional[List[str]] = None,
        verbose: Literal[0, 1, 2, 3] = 0,
    ) -> None:
        sys.modules[name] = None

        self.__name = name
        self.__ignored_attrs: Set[str] = set()
        self.__logger: Optional["logging.Logger"] = None
        self.__module: Optional[ModuleType] = None
        self.__set_verbose(verbose)
        self.__ignore(ignore)

        parent, _, suffix = self.__name.rpartition(".")
        if parent:
            register(parent, ignore=[suffix], verbose=verbose)

    def __repr__(self) -> str:
        if self.__module:
            return repr(self.__module)
        if self.__ignored_attrs:
            ignore_repr = f", ignore={list(self.__ignored_attrs)}"
        else:
            ignore_repr = ""
        return f"{self.__class__.__name__}({self.__name}{ignore_repr})"

    def __getattr__(self, __name: str) -> Any:
        self.__debug_access(__name)
        if not self.__module:
            if __name in self.__skipped_attrs:
                if not sys._getframe(1).f_code.co_name == "_find_and_load_unlocked":
                    return None
            elif __name.startswith(self.__skipped_startswith):
                return None
            elif __name in self.__ignored_attrs:
                return sys.modules[f"{self.__name}.{__name}"]
            self.__wakeup(__name)
        return getattr(self.__module, __name)

    def __call__(self, *args, **kwargs) -> Any:
        self.__debug_access("__call__")
        if not self.__module:
            self.__wakeup("__call__")
        return self.__module(*args, **kwargs)

    def __wakeup(self, __name: Optional[str] = None) -> None:
        self.__import_module()
        self.__info_wakeup("__wakeup" if __name is None else __name)

    def __ignore(self, ignore: Optional[List[str]] = None) -> None:
        if ignore is not None:
            for submodule in ignore:
                if submodule not in self.__ignored_attrs:
                    register(f"{self.__name}.{submodule}", verbose=self.__verbose)
                    self.__ignored_attrs.add(submodule.partition(".")[0])

    def __import_module(self) -> None:
        for name in _get_family(self.__name):
            if isinstance(m := sys.modules[name], self.__class__):
                del sys.modules[name]
                try:
                    module = importlib.import_module(name)
                except ModuleNotFoundError:
                    module = _get_from_sys_module(name)
            else:
                module = m
        self.__module = module

    def __set_verbose(self, verbose: int) -> None:
        self.__verbose = verbose
        if verbose >= 1 and self.__logger is None:
            self.__logger_init()

    def __logger_init(self) -> None:
        logger = logging.getLogger("lazyr")
        logger.propagate = False
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)
            sh = logging.StreamHandler()
            fm = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
            sh.setFormatter(fm)
            logger.addHandler(sh)
        logger.info("register -> %s%s", self.__name, self.__get_frame_info(5))
        self.__logger = logger

    def __debug_access(self, __name: str) -> None:
        if self.__verbose >= 2:
            self.__logger.debug(
                "access -> %s.%s%s", self.__name, __name, self.__get_frame_info(3)
            )

    def __info_wakeup(self, __name: str) -> None:
        if self.__verbose >= 1:
            self.__logger.info(
                "load -> %s(.%s)%s",
                self.__name,
                __name,
                self.__get_frame_info(4),
            )

    def __get_frame_info(self, stacklevel: int) -> str:
        if self.__verbose < 3:
            return ""
        stack = traceback.extract_stack()[-1 - stacklevel]
        return (
            f"\n  file {stack.filename}, line {stack.lineno}, in {stack.name}"
            f"\n    {stack.line if stack.line else '...'}"
        )


def _get_family(name: str) -> List[str]:
    names: List[str] = [tmp := (splits := name.split("."))[0]]
    for i in splits[1:]:
        names.append(tmp := f"{tmp}.{i}")
    return names


def _get_from_sys_module(name: str) -> "ModuleType":
    if name in sys.modules:
        return sys.modules[name]
    parent, _, suffix = name.rpartition(".")
    if parent:
        return getattr(_get_from_sys_module(parent), suffix)
    raise ModuleNotFoundError(f"no module named {name!r}")
