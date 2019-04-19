# 哈工大编译器实验

### 词法分析器 Lexer
描述：	哈尔滨工业大学 编译原理 实验二 2019.4.19
		Python实现词法分析器，输出token序列表

主要功能：设计实现高级语言的词法分析器，基本功能为识别以下单词：
（1）	标识符：由大小写字母、数字、下划线组成，但必须以字母和下划线开头；
（2）	关键字：类型关键字（整型、浮点型、布尔型）；分支结构中的if、else、then，循环结构中的do、while；
（3）	运算符：算术运算符、关系运算符、逻辑运算符；
（4）	分隔符：用于结尾的“；”，左右圆括号，花括号，中括号；
（5）	常数：整数、浮点数
（6）	注释：/*……*/


### 语法分析器 Parser
描述：	哈尔滨工业大学 编译原理 实验二 2019.4.19
		Python实现语法分析器，识别由LR（1）文法产生的语言

主要功能：
（1）	存储文法的产生式，自动归类终结符与非终结符，自动计算First集、Follow集；
（2）	实现closure函数，对给定的项目集计算其闭包以及项目的展望符（lookahead）；
（3）	实现go函数，对给定的自动机状态S（i）与文法符号X，求解其转移状态S（j）；
（4）	利用closure函数与goto函数，生成识别LR（1）文法的viable prefix的自动机；
（5）	自动构建action table和goto table；
（6）	实现Parse语法分析，用符号栈和状态栈，结合action table和goto table，进行字符的shift与产生式的reduce，从而实现语法分析；
（7）	处理来自Lexer词法分析器的输入，判断语法的正确性。


#### 文法的定义：
start -> classes
##### 类
classes -> classes classes
classes -> class IDN { method }
classes -> class IDN { field method }
##### 域和方法
field -> D
field -> access D
method -> method method
method -> type IDN ( ) { P }
method -> type IDN ( args ) { P }
method -> access type IDN ( ) { P }
method -> access type IDN ( args ) { P }
##### 参数列表
args -> args , arg
args -> arg
arg -> T IDN
##### 访问控制符
access -> public
access -> private
access -> protected
##### 程序主体
P -> P P
P -> D
P -> S
S -> S S
##### 声明语句
D -> D D
D -> D S
D -> T IDN ;
D -> T M ;
M -> m
M -> M , m
m -> IDN = E ;
D -> T IDN = E ;
T -> type
T -> type [ ]
##### 数据类型
type -> int 
type -> float
type -> long
type -> double
type -> char
type -> void
##### 赋值语句
S -> IDN = E ;
S -> IDN op ;
S -> op IDN ;
op -> ++
op -> --
S -> L = E ;
##### 函数调用
S -> call ;
call -> IDN ( )
call -> IDN ( param )
param -> E
param -> param , E
##### 运算表达式
E -> E + E
E -> E * E
E -> - E
E -> ( E )
E -> IDN
E -> digit
E -> L
L -> IDN [ E ]
L -> L [ E ]
##### 函数调用
E -> call
##### 控制流语句
S -> if ( B ) { P }
S -> if ( B ) { P } else { P }
S -> while ( B ) { P }
S -> for ( S B ; IDN op ) { P }
S -> for ( S B ; IDN = E ) { P }
##### 布尔表达式
B -> B and B
B -> B or B
B -> E relop E
B -> true
B -> false
##### 关系运算符
relop -> <
relop -> <=
relop -> ==
relop -> !=
relop -> >
relop -> >=
relop -> &&







