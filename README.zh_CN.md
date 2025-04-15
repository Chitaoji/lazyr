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
举个例子，我们试试把 *numpy* 变成懒模块：

```py
>>> import lazyr
>>> lazyr.register("numpy") # 注册numpy为懒模块
LazyModule(numpy) # 这就是numpy所对应的LazyModule对象

>>> import numpy as np # 由于numpy已被注册为懒模块，这条语句不会真正导入numpy 
>>> np
LazyModule(numpy) # np被赋值为numpy所对应的LazyModule对象

>>> arr = np.array([]) # 由于属性被访问，numpy被激活和加载
>>> np
<module 'numpy' from '/../..'>
```

以下是一种更加简洁的写法, 但可能导致 *type hints* 失效：

```py
>>> np = lazyr.register("numpy")
```

### 检查模块

使用函数 `islazy()` 以检查一个模块是否为尚未激活的懒模块：

```py
>>> scipy = lazyr.register("scipy")
>>> lazyr.islazy(scipy)
True
```

### 激活模块

一旦模块的属性被访问，懒模块将被自动激活和加载。如果想要主动地强制激活模块，可以使用 `wakeup()` 函数：

```py
>>> lazyr.wakeup(scipy) # scipy被强制激活
>>> lazyr.islazy(scipy)
False
```

### 属性忽略

您可以通过设置 `register()` 的 `ignore` 参数来忽略掉一些子模块。只需输入待忽略子模块的名称列表，这些子模块也将被注册为懒模块（与主模块一起）。

```py
>>> lazyr.register("pandas", ignore=["DataFrame", "Series"]) # 除了pandas本身，还忽略子模块DataFrame和Series
LazyModule(pandas, ignore=['DataFrame', 'Series'])
```

以上语句和下面两行代码有大致相同的作用：

```py
>>> _, _ = lazyr.register("pandas.DataFrame"), lazyr.register("pandas.Series")
```

### 列出懒模块

使用 `listall()` 列出系统中所有未激活的懒模块：

```py
>>> lazyr.listall()
[LazyModule(pandas, ignore=['Series', 'DataFrame']), LazyModule(pandas.DataFrame), LazyModule(pandas.Series)]
```

### 日志

在调用 `register()` 时指定 `verbose` 参数，可以看到关于模块的日志：

```py
>>> _ = lazyr.register("matplotlib.pyplot", verbose=2)
INFO:lazyr:import:matplotlib.pyplot
INFO:lazyr:import:matplotlib

>>> import matplotlib.pyplot as plt
DEBUG:lazyr:access:matplotlib.pyplot.__spec__
DEBUG:lazyr:access:matplotlib.__spec__
DEBUG:lazyr:access:matplotlib.pyplot

>>> plot = plt.plot
DEBUG:lazyr:access:matplotlib.pyplot.plot
INFO:lazyr:load:matplotlib.pyplot(.plot)
```

## 链接
### Github 仓库
* https://github.com/Chitaoji/lazyr/

### PyPI 项目
* https://pypi.org/project/lazyr/

## 许可
本项目遵循 BSD 3-Clause 许可证.
