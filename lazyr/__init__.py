import importlib
import inspect
import sys
from typing import TYPE_CHECKING, Any, List, Literal, Optional

if TYPE_CHECKING:
    from types import ModuleType

__all__ = ["register"]


def register(
    name: str,
    package: Optional[str] = None,
    ignore: Optional[List[str]] = None,
    verbose: Literal[0, 1, 2, 3] = 0,
) -> "ModuleType":
    """
    Register a module as a lazy one, which is only imported when its attributes are
    being accessed.

    Parameters
    ----------
    name : str
        Name of the module.
    package : Optional[str], optional
        Required when performing a relative import. It specifies the package to use
        as the anchor point from which to resolve the relative import to an absolute
        import, by default None.
    ignore : Optional[List[str]], optional
        Specified the ignored attrbutes. When an ignored attribute is accessed, the
        module will still remain unimported. By default None.
    verbose : Literal[0, 1, 2, 3], optional
        Specifies the level of verbosity for debugging. It accepts values from 0 to 3.
        By default 0.

    Returns
    -------
    ModuleType
        The registered module. Use it as a normal one.

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
        m._LazyModule_ignore(ignore)
    return sys.modules[module_name]


def __join_module_name(name: str, package: Optional[str] = None):
    if package is None:
        package = ""
    elif not name.startswith("."):
        raise TypeError(
            f"expected a relative import when the `package` argument is provided, got '{name}' instead"
        )
    return package + name


class LazyModule:
    __skipped = {
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
        """
        A lazy module.

        """
        self.__name = name
        self.__ignored = {} if ignore is None else set(ignore)
        self.__verbose = verbose
        self.__module: Optional[ModuleType] = None

        if p := self.__get_parent():
            register(p, ignore=[self.__get_suffix()], verbose=verbose)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__name}, ignore={self.__ignored})"

    def __getattr__(self, __name: str) -> Any:
        self.__debug_access(__name)
        if self.__module is None:
            if __name in self.__skipped:
                return NotImplemented
            if __name in self.__ignored:
                if (module_name := f"{self.__name}.{__name}") in sys.modules:
                    return sys.modules[module_name]
                return NotImplemented
            if self.__import_module():
                self.__debug_import(__name)
        return getattr(self.__module, __name)

    def _LazyModule_ignore(self, ignore: Optional[List[str]] = None) -> None:
        self.__ignored |= {} if ignore is None else set(ignore)

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
            print(f"accessing `{self.__name}.{__name}`{self.__get_frame_info()}")

    def __debug_import(self, __name: str) -> None:
        if self.__verbose >= 1:
            print(
                f"`{self.__name}` is imported with attribute `{__name}`{self.__get_frame_info()}"
            )

    def __get_frame_info(self) -> str:
        if self.__verbose < 3:
            return ""
        f = inspect.stack()[3]
        return (
            f" by '{f[1]}' -> {f[4][0].strip() if isinstance(f[4], list) else None!r}"
        )

    def __get_family(self) -> List[str]:
        names: List[str] = []
        return [".".join(names := names + [i]) for i in self.__name.split(".")]

    def __get_parent(self) -> str:
        return self.__name.rpartition(".")[0]

    def __get_suffix(self) -> str:
        return self.__name.rpartition(".")[-1]
