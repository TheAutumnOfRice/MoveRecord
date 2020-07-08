from MoveRecord import moveset
"""
Example 4：
moveset的嵌套
使用moveset.wset函数Wrap一个moveset，
使得一个moveset可以调用另一个moveset中的内容。
ms.wset(ms:要运行的moveset,nextid:下一步ID,static:静态变量区,initvar:初值改变)

嵌套规则
1   上层moveset被称为parent
2   子moveset可以通过var["__parent__"]来访问parent.var
3   parent可以通过var["__moveset__XXX"]，其中XXX为子moveset的name，来访问子moveset的变量区域
4   __parent__参数只在子moveset中存在，顶层moveset的var中不含该参数
5   __parent__参数为只读参数，修改__parent__没有意义且可能导致错误
    在存储时，__parent__不会被储存到文件。
6   必须先定义，再wset。先wset，再定义可能会出现莫名其妙的错误

static：静态变量
1   当static设置为False（默认）时，子moveset运行完毕后将把自己的变量全部清除
2   若static设置为True，则运行完毕后将保留自己的变量区
    这样，parent也可以读写自己的变量，下一次进入时依然可以继续上一次的变量区
    
initvar：初值设置
1   initvar为一个Dict[key:value]的类型，表示将变量key的初值设置为value
2   注意：此处的初值为“运行moveset”后的值，如果原来已经有存档值，则该值【会被初值覆盖】
3   默认initvar为None，表示不特殊设置子moveset的初值
    此时，子moveset变量区的值全部为存档值或原本设定的初值
4   如果手动修改了initvar，则在子moveset运行前会用initvar的值更新moveset.var
5   设置__start__初值，可以修改子moveset的入口ID
6   设置__current__初值，可以强制运行子moveset中的某一条指定ID
    与修改__start__不同的是，如果子moveset已经执行过，__current__会影响到存档中的执行记录，
    而__start__只对第一次执行起效果
"""

def Fun(title,var):
    print("这里是",title)
    print("将x增加1")
    var["x"]+=1
    print("现在x的值为",var["x"])
    input("按下回车继续...")

def Again(var):
    a=input("是否继续？[Y]/N")
    if a=="N":
        return False
    else:
        return True
if __name__=="__main__":
    msA=moveset("moveA",use_json=True)
    msA.addvar("x",0)
    msA.addmove(0,msA.wv(Fun,"__exit__",title="movesetA"),True)

    msB=moveset("moveB",use_json=True)
    msB.addvar("x",0)
    msB.addmove(0,msB.wv(Fun,"__exit__",title="movesetB"),True)

    ms=moveset("example4",use_json=True)
    ms.addmove(0,ms.w("print('Hello world!')",1),True)

    # 接下来运行msA，如果不加修改，则默认从msA的__start__入口运行
    ms.addmove(1,ms.wset(msA,2))

    # 接下来运行msB
    # 由于msB的static设置为True，则在msB运行结束后，其变量区不会被删除
    # 这意味着可以从上层读取B中的变量
    # 也意味着下一次运行到msB时，之前的变量将保留
    ms.addmove(2,ms.wset(msB,3,static=True))

    ms.addmove(3,ms.wif(Again,1,"__exit__"))

    ms.run("rec",continue_=False)

