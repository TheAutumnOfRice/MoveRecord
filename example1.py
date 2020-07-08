from MoveRecord import moveset
"""
Example 1：
自行构造MoveFun函数，
使用addmove方法手动创建moveset

MoveFun函数要求：
1   MoveFun有且只有一个参数var:Dict，用来读取变量区的内容
2   MoveFun返回值为IDType类型，这可以是一个int也可以是一个str，表示运行结束后跳转的ID
    如果需要结束moveset，则返回值为"__exit__"
    
变量区介绍
1   变量存储在moveset.var中，是一个dict类型
2   var中常驻变量包括：
    a)  __start__ 代表moveset执行时的入口函数的ID
    b)  __current__ 代表moveset当前执行中的函数ID
    c)  __return__ 代表moveset结束执行时返回的值
    d)  __parent__ 对于子moveset，其父亲。该变量【只读】，且不会被保存在文件。切勿修改
    e)  __stack__ 错误判断机制中用于暂存出错地点的current。该变量【只读】，切勿修改
3   可以通过moveset.addvar(变量名，初始值)方法添加一个变量
    该变量将在moveset运行前按照初值进行初始化 (setdefault)
    如果以continue模式运行，则变量区的值以上一次变量的值为准

"""

def MoveFun1(var):
    print("普通的函数")
    input("按下回车继续...")
    return 2

def MoveFun2(var):
    print("对变量区进行操作的函数:对返回值进行自加")
    var["__return__"] += 1
    print("当前返回值为",var["__return__"])
    input("按下回车继续...")
    return 3

def MoveFun3(var):
    print("分支函数，输入0从MoveFun运行，输入1则结束moveset")
    p=input("请输入数字：")
    return 1 if p=="0" else "__exit__"

if __name__ == "__main__":
    # 创建一个名称为example1的moveset
    # use_json设置为True方便调试（用记事本打开rec文件即可）
    ms=moveset("example1",use_json=True)
    # addmove导入函数列, addmove(move的ID，MoveFun类型函数)
    ms.addmove(1,MoveFun1,start=True)  # start设为True，表示该函数为moveset的入口函数
    ms.addmove(2,MoveFun2)
    ms.addmove(3,MoveFun3)
    # 初始化返回值为10
    ms.addvar("__return__",10)
    # 运行脚本 ms.run(运行位置)
    # continue_设为True表示继续运行上次未完成的脚本，可以在run过程中手动重启程序查看保存效果
    # continue_设为False时，将无视上次存储记录重新运行
    # 可以手动指定start参数来更改程序入口
    r=ms.run("rec",continue_=True)
    print("ms的返回值为",r)
