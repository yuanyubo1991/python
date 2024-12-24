@[toc](目录)



# 字符串

- 字符串按需用单引号或双引号包起来

```python
var1 = 'He said, "good idle!"'
var2 = "i'm chinese."
```

- 字符串中每个单词首字母大写

```python
var1.title()
```

- 字符串中每个单词全部字母大写

```python
var1.upper()
```

- 字符串中每个单词全部字母小写

```python
var1.lower()
```

```python
- 字符串拼接
```

```python
var3 = var1 + var2
print(var3)
```

```python
var3 += 'additional ending'
print(var3)
```

```python
- 字符串中可以包含转义字符
```



  var5 = '     Here list the member:\nJam\tJohn    '

- 去除字符串末尾的空白
  var5.rstrip()

- 去除字符串开头的空白
  var5.lstrip()

- 去除字符串开头和末尾的空白
  var5.strip()

- 数值类型转为字符串类型
  a = 20
  b = str(a)

- 字符串类型转为数值类型
  a = '30'
  b = int(a)

- 获取字符串长度

a = 'good morning!'
len(a)

# 列表

- 定义
  
  ```python
  var = ['we', 'are', 23]
  ```

- 访问列表元素
  
  ```python
  var[0]
  var[1] 
  var[2] 
  var[-1] 
  var[-2]
  var[-3]
  ```

- 列表元素按字母重排序
  
  ```python
  var.sort()
  var.sort(reverse=True)
  ```

- 反转列表元素顺序
  
  ```python
  var.reverse()
  ```

- 获取列表长度
  
  ```python
  len(var)
  ```

- 在列表末尾添加新元素
  
  ```
  var.append('years')
  ```

- 在列表任意位置插入新元素
  
  ```pyth
  var.insert(1, 'all')
  ```

- 删除列表中某个元素
  
  ```python
  del var[1]
  ```

- 弹出列表中某个元素
  
  ```python
  var1 = var.pop(1)
  ```
  
  _说明：pop不指定元素位置时默认弹出末尾元素_

- 根据值删除列表中某个元素
  
  ```python
  var.remove('we')
  ```

- 列表切片
  
  ```python
  var[1:2]
  var[:2]
  var[1:]
  ```

- 复制列表
  
  ```python
  var1 = var[:]
  ```
  
  _说明：复制列表不能用var1 = var，这样还是只有一个列表，只是新增了一个指向该列表的指针而已_

- 遍历列表
  
  ```python
  for variable in var:
      print(variable)
  ```
  
  _使用for循环遍历列表时，不要在循环代码块中修改列表，如果要这样做，使用while循环_

# 元组

- 定义
  
  ```python
  var = ('we', 'are')
  ```
  
  _说明：和列表的区别是，其元素不可修改，其它用法和列表相同_

# 字典

- 定义空字典
  
  ```python
  var = {}
  ```

- 访问字典元素
  
  ```python
  var['age']
  ```

- 添加键-值对
  
  ```python
  var['job'] = 'engineer'
  ```

- 删除键-值对
  
  ```python
  delvar['job']
  ```

- 遍历字典
  
  ```python
  for key, value in var.items():
  
  for key in var.keys():
  
  for value in var.values():
  ```
  
  

# if条件语句

- 示例1
  
  ```python
  for variable in var:
      if variable == 'are':
          print(variable.upper())
      elif variable == 'we':
          print(variable.lower())
      else:
          print(variable.title())
  ```

- 示例2
  
  ```python
  if 'are' in var:
      print(var)
  
  if 'are' not in var:
      print(var)
  
  if age >= 18:
      print(var)
  
  if var:    #if var is not empty
      print(var)
  ```

# while循环

```python
while current_number <= 5:
    print(current_number)
    current_number += 1


while message != 'quit':
    message = input(prompt)
    print(message)


active = True
while active:
    message = input(prompt)
    if message == 'quit':
        active = False
    else:
        print(message)


while True:
    city = input(prompt)
    if city == 'quit':
        break
    else:
        print("I'd love to go to " + city.title() + "!")


while current_number < 10:
    current_number += 1
    if current_number % 2 == 0:
        continue
    print(current_number)
```

# 系统函数

range(1,5,2)：用于产生1到5之间的整数，步长为2

var = list(range(1,5,1))：将产生的整数转换成列表

min(var)：找到数字列表中元素的最小值

max(var)：找到数字列表中元素的最大值

sum(var)：计算数字列表中所有元素的和

squares = [var**2 for var in range(1,11)]

set(var)去除列表中重复元素

message = input(“please input something”)接受用户输入信息

split()将字符串拆分成列表，以空格为分隔符：var.split()

# 自定义函数

def greet_users(names):

for name innames:

msg = "Hello, " + name.title() + "!"

print(msg)

usernames = ['hannah', 'ty', 'margot']

greet_users(usernames)

参数为列表时，默认是将源列表传进函数，函数可以修改源列表，如果不想在函数中修改源列表，则传递列表副本：

def function_name(format_var[:])

       print(format_var)

function_name(real_var[:])

传递任意数量的实参：

def make_pizza(*toppings):

       print(toppings)

make_pizza('pepperoni')

make_pizza('mushrooms', 'green peppers','extra cheese')

形参名*toppings 中的星号让Python创建一个名为toppings 的空元组，并将收到的所有值都封装到这个元组中。

如果要让函数接受不同类型的实参，必须在函数定义中将接纳任意数量实参的形参放在最后。Python先匹配位置实参和关键字实参，再将余下的实参都收集到最后一个形参中。

def build_profile(first, last,**user_info):

形参**user_info 中的两个星号让Python创建一个名为user_info 的空字典，并将收到的所有名称—值对都封装到这个字典中。

可以将函数存储在称为模块的独立文件中，再使用import语句将模块导入主程序。通过将函数存储在独立的文件中，可隐藏程序代码的细节，将重点放在程序的高层逻辑上。这还能让你在众多不同的程序中重用函数。将函数存储在独立文件中后，可与其他程序员共享这些文件而不是整个程序。

名为pizza.py的文件中包含如下代码：

def make_pizza(size, *toppings):

print("\nMakinga " + str(size) +"-inch pizza with the following toppings:")

for topping intoppings:

print("- " + topping)

在另一个文件中：

import pizza

pizza.make_pizza(16, ‘pepperoni’)

代码行import pizza 让Python打开文件pizza.py，并将其中的所有函数都复制到这个程序中。你看不到复制的代码，因为这个程序运行时，Python在幕后复制这些代码。

也可以只导入模块中的特定函数：

from module_name import function_name1,function_name2

这种导入方式，在调用函数时，无需指定module_name

from pizza import make_pizza as mp

mp(16, 'pepperoni')

mp(12, 'mushrooms', 'green peppers', 'extracheese')

import pizza as p

p.make_pizza(16, 'pepperoni')

p.make_pizza(12, 'mushrooms', 'greenpeppers', 'extra cheese')

from pizza import *

make_pizza(16, 'pepperoni')

make_pizza(12, 'mushrooms', 'greenpeppers', 'extra cheese')

如果程序或模块包含多个函数，可使用两个空行将相邻的函数分开，这样将更容易知道前一个函数在什么地方结束，下一个函数从什么地方开始。

# 嵌套

列表中的元素可以是字典类型，也就是说多个字典类型元素组成一个字典列表

字典的键-值对，值可以是个列表

列表嵌套字典，字典嵌套列表，字典嵌套字典

# 类

定义类时，在方法__init__中通过self.xxx声明的变量为类的全局变量，称为属性。

实例化类时，例如my_dog = dog(‘jack’, 15)，python会自动：

（1）调用dog的方法__init__

（2）将指向实例my_dog本身的指针作为实参，传递给dog类中的形参self

（3）将实例化时指定的实参’jack’和15，分别传递给dog类中__init__的形参a和b

实例化类之后，可以用my_dog.name的方式访问实例化类中的属性，也可修改属性的值

编写类时，并非总是要从空白开始。如果你要编写的类是另一个现成类的特殊版本，可使用继承。一个类继承 另一个类时，它将自动获得另一个类的所有属性和方法；原有的类称为父类，而新类称为子类。子类继承了其父类的所有属性和方法，同时还可以定义自己的属性和方法。创建子类时，父类必须包含在当前文件中，且位于子类前面。定义子类时，必须在括号内指定父类的名称。

在子类的__init__中，可以新增属性

在子类中，可以重写父类的方法

一个类的实例化可以作为另一个类的属性：

class Battery():

def__init__(self, battery_size):

self.battery_size = battery_size

def describe_battery(self):

print("This car has a " + str(self.battery_size) +"-kWh battery.")

class ElectricCar(Car):

def__init__(self, make, model, year):

super().__init__(make, model, year)

self.battery = Battery(70)

my_tesla = ElectricCar('tesla', 'model s',2016)

print(my_tesla.get_descriptive_name())

my_tesla.battery.describe_battery()

Python允许你将类存储在模块中，然后在主程序中导入所需的模块。导入方法和函数一样


# 文件

打开文件：with open(file_path) as file_object

读取文件：file_object.read()



逐行读取文件：



写入文件：
再调用open()函数时提供一个实参’w’或者是’a’
w：每次打开时覆盖文件中原有内容
a：每次打开时保留文件中原有内容，新内容附加到文件末尾


# 异常

Python使用被称为异常 的特殊对象来管理程序执行期间发生的错误。每当发生让Python不知所措的错误时，它都会创建一个异常对象。如果你编写了处理该异常的代码，程序将继续运行；如果你未对异常进行处理，程序将停止，并显示一个traceback，其中包含有关异常的报告。异常是使用try-except 代码块处理的。try-except 代码块让Python执行指定的操作，同时告诉Python发生异常时怎么办。使用了try-except 代码块时，即便出现异常，程序也将继续运行：显示你编写的友好的错误消息，而不是令用户迷惑的traceback。

通过将可能引发错误的代码放在try-except 代码块中，可提高这个程序抵御错误的能力。依赖于try 代码块成功执行的代码都应放到else 代码块中。

Python有一个pass 语句，可在代码块中使用它来让Python什么都不要做。

filename = 'alice.txt'

try:

withopen(filename) as f_obj:

contents = f_obj.read()

except FileNotFoundError:

msg ="Sorry, the file " + filename + " does not exist."

print(msg)

else:

words =contents.split()

num_words =len(words)

print("Thefile " + filename + " has about " + str(num_words) + "words.")

# 执行

__name__是python的一个内置类属性，是标识模块的名字的一个系统变量。

python的模块既可以被调用，也可以独立运行，这点不像C++和C的头文件。

如果当前模块被直接执行（主模块），__name__存储的是__main__

如果当前模块是被调用的模块（被导入），则__name__存储的是py文件名（模块名称）

通过区分__name__存储的值，python就可以分清楚哪些是主函数，进入主函数执行，并且可以调用其他模块中的函数、变量等。

# 模块

## argparse

- 功能
  解析命令行选项和参数

- 导入模块
  
  ```python
  import argparse
  ```

- 创建命令行解析器对象
  
  ```python
  var = argparse.ArgumentParser(description='here creat a new parser')
  ```

- 为解析器对象添加需要解析的命令行参数
  
  ```python
  var.add_argument('-opt1', dest='opt1_param', type=str, default='opt1 default value')
  var.add_argument('-opt2', dest='opt2_param', type=int, default=20, choices=[10, 20, 30])
  var.add_argument('-f1', dest='flag1', default=False, action='store_true')
  var.add_argument('-f2', dest='flag2', default=False, action='store_false')
  ```
  
  - -opt1, -opt2, -f1, -f2: 定义的命令行选项缩写
  
  - dest：指定解析后的参数名称
  
  - type：命令行参数值的类型
  
  - default： 命令行参数的默认值
  
  - action：只适用于flag类型（不带参数值）的命令行选项，定义当命令行指定该选项时的动作
  
  - choices：指定允许的参数值列表

- 解析命令行参数的值
  
  ```python
  arg_list = var.parse_args() #这里返回的是类
  var1 = arg_list.opt1
  var2 = arg_list.opt2
  ```

## JASON

模块json能够将简单的Python数据结构转储到文件中，并在程序再次运行时加载该文件中的数据。还可以使用json在Python程序之间分享数据。更重要的是，JSON数据格式并非Python专用的，能够将以JSON格式存储的数据与使用其他编程语言的人分享。JSON（JavaScript Object Notation）格式最初是为JavaScript开发的，但随后成了一种常见格式，被包括Python在内的众多语言采用。通常使用文件扩展名.json来指出文件存储的数据为JSON格式

函数json.dump()：将数据存储到文件中

函数json.load()：读取文件中的数据

import json

username = input("What is your name?")

filename = 'username.json'

with open(filename, 'w') as f_obj:

json.dump(username,f_obj)

print("We'llremember you when you come back, " + username + "!")

import json

filename = 'username.json'

with open(filename) as f_obj:

username =json.load(f_obj)

print("Welcomeback, " + username + "!")
