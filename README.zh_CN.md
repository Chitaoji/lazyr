# lazyr

一个创建懒加载 (lazily-imported) 模块的工具。

懒加载模块在import的时候不会被实际加载到 Python 环境中，只有在其属性被访问时，才会实际加载。当您导入一些几乎不会使用，但加载耗时很久的模块时，可以使用懒模块，节约程序的初始化时间。

## README.md

* en [English](README.md)
* zh_CN [简体中文](README.zh_CN.md)

## 安装

```sh
$ pip install lazyr
```

## 用例
### 创建懒模块
举个例子，我们试试把 *pandas* 变成懒模块：

```py
>>> import lazyr
>>> lazyr.register("pandas") # 注册pandas为懒模块
LazyModule(pandas) # 这就是pandas所对应的LazyModule对象

>>> import pandas as pd # 由于pandas已被注册为懒模块，这条语句不会真正导入pandas 
>>> pd
LazyModule(pandas) # pd被赋值为pandas所对应的LazyModule对象

>>> df = pd.DataFrame # 由于属性被访问，pandas被激活和加载
>>> pd
<module 'pandas' from '/../..'>
```

以下是一种更加简洁的写法, 但可能导致 *type hints* 失效：

```py
>>> import lazyr
>>> pd = lazyr.register("pandas")
>>> pd
LazyModule(pandas)
```

### 检查模块

使用函数 `islazy()` 以检查一个模块是否为尚未激活的懒模块：

```py
>>> lazyr.islazy(pd)
True
```

### 激活模块

一旦模块的属性被访问，懒模块将被自动激活和加载。如果想要主动地强制激活模块，可以使用 `wakeup()` 函数：

```py
>>> lazyr.wakeup(pd) # pandas被强制激活
>>> lazyr.islazy(pd)
False
```

### 属性忽略

您可以通过设置 `register()` 的 `ignore` 参数来忽略掉一些子模块。只需输入待忽略子模块的名称列表，这些子模块也将被识别为懒模块（与主模块一起）。

```py
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"]) # 除了pandas本身，还忽略子模块DataFrame和Series
LazyModule(pandas, ignore=['DataFrame', 'Series'])
```

以上语句和下面两行代码有同样的作用：

```py
>>> lazyr.register("pandas.DataFrame")
LazyModule(pandas.DataFrame)
>>> lazyr.register("pandas.Series")
LazyModule(pandas.Series)
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
