"""
Creates lazy modules in a more readable and safer way.

"""
import importlib
import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Set

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
        Specifies the ignored attrbutes of the lazy module. When an ignored attribute
        is accessed, the lazy module will still remain inactivated. By default None.
    verbose : Literal[0, 1, 2, 3], optional
        Specifies the level of verbosity for debugging. It accepts values from 0 to 3.
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
        package = ""
    elif not name.startswith("."):
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

    __skipped: Set = {
        "__spec__",
        "__path__",
        "_ipython_canary_method_should_not_exist_",
    }

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

        if p := self.__get_parent():
            register(p, ignore=[self.__get_suffix()], verbose=verbose)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.__name}, ignore={self.__ignored_attrs})"
        )

    def __getattr__(self, __name: str) -> Any:
        if __name.startswith("!"):
            return getattr(self, f"_{self.__class__.__name__}__{__name[1:]}")
        self.__debug_access(__name)
        if self.__module is None:
            if __name in self.__skipped:
                if not sys._getframe(1).f_code.co_name == "_find_and_load_unlocked":
                    return None
            elif __name in self.__ignored_attrs:
                if (module_name := f"{self.__name}.{__name}") in sys.modules:
                    return sys.modules[module_name]
                return None
            self.__wakeup(__name)
        return getattr(self.__module, __name)

    def __wakeup(self, __name: Optional[str] = None) -> None:
        if self.__import_module():
            self.__debug_import("__wakeup" if __name is None else __name)

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

    def __debug_access(self, __name: str) -> None:
        if self.__verbose >= 2:
            logging.warning(
                "accessing `%s.%s`%s", self.__name, __name, self.__get_frame_info(3)
            )

    def __debug_import(self, __name: str) -> None:
        if self.__verbose >= 1:
            logging.warning(
                "`%s` is loaded with attribute `%s`%s",
                self.__name,
                __name,
                self.__get_frame_info(4),
            )

    def __get_frame_info(self, depth: int) -> str:
        if self.__verbose < 3:
            return ""
        f = inspect.stack()[depth]
        return f" by '{f[1]}': {f[3]}: {f[4][0].strip() if isinstance(f[4], list) else None!r}"

    def __get_family(self) -> List[str]:
        names: List[str] = []
        return [".".join(names := names + [i]) for i in self.__name.split(".")]

    def __get_parent(self) -> str:
        return self.__name.rpartition(".")[0]

    def __get_suffix(self) -> str:
        return self.__name.rpartition(".")[-1]
