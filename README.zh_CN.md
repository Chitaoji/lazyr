# lazyr

一个创建懒加载 (Lazy-Importing) 模块的工具。

懒加载模块在其属性被访问之前不会被实际加载到 Python 环境中。当您导入一些几乎不会使用，但加载耗时很久的模块时，使用懒模块可以节约程序的初始化时间。

## README.md

* en [English](README.md)
* zh_CN [简体中文](README.zh_CN.md)

## 安装

```sh
$ pip install lazyr
```

## 用法
### 创建懒模块
作为例子，我们试着把 *pandas* 变为懒模块：

```py
>>> import lazyr
>>> lazyr.register("pandas") # 注册pandas为懒模块
LazyModule(pandas)

>>> import pandas as pd # 由于pandas已被注册为懒模块，这条语句实际不起作用 
>>> pd # pandas会显示为一个LazyModule对象
LazyModule(pandas)

>>> df = pd.DataFrame # 由于属性被访问，pandas此时被激活和加载
>>> df
<class 'pandas.core.frame.DataFrame'>
```

以下是一种更加简洁的写法, 但可能导致 *type hints* 失效：

```py
>>> import lazyr
>>> pd = lazyr.register("pandas")
>>> pd
LazyModule(pandas)
```

### 检查模块是否为懒

使用函数 `islazy()` 以检查一个模块是否为懒模块：

```py
>>> lazyr.islazy(pd)
True
```

### 激活模块

一旦模块的属性被访问，懒模块将被自动激活和加载。如果想要主动地强制激活模块，可以使用 `wakeup()` 函数：

```py
>>> lazyr.wakeup(pd) # pandas被激活
>>> lazyr.islazy(pd)
False
```

### 属性忽略

您可以通过设置 `register()` 的 `ignore` 参数来忽略掉一些属性。您需要输入待忽略属性的名称列表，这些属性将被模块自动忽略：它们的值将被设置为None，并且对它们的访问将不再导致懒模块被激活。

```py
>>> import lazyr
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"]) # 忽略两个属性：DataFrame和Series
LazyModule(pandas, ignore=['DataFrame', 'Series'])

>>> from pandas import DataFrame # DataFrame已被忽略，pandas未加载，DataFrame=None
>>> from pandas import Series # Series已被忽略，pandas未加载，Series=None
>>> from pandas import io # io不是被忽略的属性，所以pandas被加载

>>> from pandas import DataFrame # 从此DataFrame等被忽略的属性也可以正常使用了
>>> DataFrame
<class 'pandas.core.frame.DataFrame'>
```

### 日志


在调用 `register()` 时指定 `verbose` 参数，可以看到关于模块的日志：

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

## 链接
### Github 仓库
* https://github.com/Chitaoji/lazyr/

### PyPI 项目
* https://pypi.org/project/lazyr/

## 许可
本项目遵循 BSD 3-Clause 许可证.

## 更新历史

### v0.0.16
* New function `islazy()`, for checking the status of a module.
* Improved the representational strings of lazy modules.

### v0.0.15
* Various improvements.

### v0.0.12
* Prettier logs.

### v0.0.11
* Fixed the meta-data.
* Performance enhancements.

### v0.0.9
* Updated LICENSE.

### v0.0.7
* Removed unnecessary objects from the main `lazyr` namespace.

### v0.0.6
* Improved logging:
    * Created a separate logger named 'lazyr' for lazy modules;
    * More detailed logs when `verbose` > 0.

### v0.0.4
* `LazyModule` no longer activated by `_ipython_*()` or `_repr_*()` methods.

### v0.0.3
* Various improvements.

### v0.0.2
* New function `wakeup()`, for compulsively activating modules.

### v0.0.1
* Initial release.
