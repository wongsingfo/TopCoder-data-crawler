TC-data
===

A script for crawling testing data from TopCoder.


使用说明
=====

下载并运行
-----

对于windows操作系统：在[release标签](https://github.com/wangck1998/TC-data/releases)下可以找到用pyinstaller编译好的文件。下载后解压，运行`get.exe`（命令行程序）。

对于Linux/Unix和Max OS X：下载`get.py`  文件，赋予运行权限，运行`./get.py`就可以了。

layout文件配置
----

layout文件用于表示数据的格式，其中`layout.in`表示输入数据的格式，`layout.out`表示输出数据的格式。layout文件需要放在和`get.exe`相同的目录下。下面拿输入数据做说明。

TC的题目都有这样的说明（以某题为例）：

```tex
Definition
    	
	Class:	FourLamps
	Method:	count
	Parameters:	String, int
	Returns:	long
	Method signature:	long count(String init, int k)
	(be sure your method is public)
```

其中Parameters一项说明了输入的数据，我们可以看到Examples有：

```tex
Examples
0)	
	"0001"
	2
	Returns: 4
```

假如我们想把上面的数据生成为（下面的4表示字符串的长度）：

```tex
4 2
0001
```

我们可以往`layout.in`文件写入：

```tex
A. B
A
```

其中的**大写字母**依次被绑定到参数上，这里A被绑定到String上，B被绑定到int上。字母后面加点有特殊的含义，现列举如下：

对于字母加一个点：

- 数据类型是String，表示String的长度；
- 数据类型是数组，表示数组的长度。

对于字母加两个点：

- 数据类型是字符串数组，表示数组第一个字符串的长度（如果数组里没有元素，程序会抛出错误）。

对于字母不带点：

- 数据类型是整数，表示该整数；
- 数据类型是字符串，表示该字符串；
- 数据类型是整数数组，表示依次输出该数组的元素，用空格分隔；
- 数据类型是字符串数组，表示依次输出该数组的元素，用系统默认换行符分隔。

配置好了layout之后
----

运行程序，根据提示操作，这里举个例子：

```tex
$ ./get.py
problem url:https://community.topcoder.com/stat?c=problem_statement&pm=14643&rd=16933&rm=&cr=40168949
send request https://community.topcoder.com/stat?c=problem_statement&pm=14643&rd=16933&rm=&cr=40168949
send request http://community.topcoder.com/tc?module=ProblemDetail&rd=16933&pm=14643
send request http://community.topcoder.com/stat?c=problem_solution&cr=40168949&rd=16933&pm=14643
*** Remember to configure the layout files. ***
file name:data
group size:4
```

如果提示`please login`，那就输入用户名和密码就可以了。

这里group size是指数据分组，表示每一组数据内含有多少个子数据，特别的，如果每一组数据中都只有一组数据，则不自动输入数据组数。

生成的数据在`get.exe`所在的目录下。

常见问题
==========

- 我怎么输入不了密码？

平时的软件输入密码以*号代替，但这里不显示任何字符，输入完后按回车就可以了。

- 多组数据时，相邻两组之间没有回车！

在layout文件末尾加个回车。

- 登陆不了。

可能的原因：错误的用户名或密码，该题没有人通过，等等。

- 无缘无故就出错了。。。

这个代码几乎没有任何错误处理，所以程序非常不友好  :-(。您可以尝试在终端运行（这样可以看到错误原因），然后把出错的信息告诉我，或者发布issues。