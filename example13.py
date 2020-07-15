from MoveRecord import moveset

"""
Example 13：
2020-07-15更新：更加优美的单函数逻辑实现
使用moveset.savevar
对于需要使用T_forcestart的函数都可以使用以下优美写法。
可以对var随心操作后，保存。
这样写，效率更高，写法也更简洁。

对Example 10进行改进：
假设现在有如下逻辑：
A->B->C->D->E->F->G->H
其中A,B为进入必做，此后：
如果C已经做过，则从E开始。
F也为进入必做，这意味着如果在G崩盘了，
需要A->B->F->G重回，而在H点崩盘了，则时
A->B->F->H返回。
"""


def FunA():
    print("函数A")
    input("按下回车继续...")


def FunB():
    print("函数B")
    input("按下回车继续...")


def FunC():
    print("函数C")
    input("按下回车继续...")


def FunD():
    print("函数D")
    input("按下回车继续...")


def FunE():
    print("函数E")
    input("按下回车继续...")


def FunF():
    print("函数F")
    input("按下回车继续...")


def FunG():
    print("函数G")
    input("按下回车继续...")


def FunH():
    print("函数H")
    input("按下回车继续...")


def LogicFun(var):
    # 调用wvar函数，构造var操作类movevar。
    mv = moveset.wvar(var)
    # mv含有autosave参数，默认为True，此时setflag,clearflags后自动接mv.save保存工作区（等价ms.savestate）
    FunA()
    FunB()
    if mv.notflag("FIN_C"):
        FunC()
        mv.setflag("FIN_C")
        FunD()
    if mv.notflag("FIN_E"):
        FunE()
        mv.setflag("FIN_E")
    FunF()
    if mv.notflag("FIN_G"):
        FunG()
        mv.setflag("FIN_G")
    if mv.notflag("FIN_H"):
        FunH()
        mv.setflag("FIN_H")
    mv.clearflags()


if __name__ == "__main__":
    ms = moveset("example13")
    ms.addmove("logic", ms.wv(LogicFun, "__exit__"), True)
    ms.run("rec", True)
