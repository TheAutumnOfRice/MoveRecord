from MoveRecord import moveset

"""
Example 10：
一个比较复杂的断点逻辑例

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


if __name__ == "__main__":
    ms = moveset("example10")

    ENT = ms.startw(FunA)
    ms.T_forcestart(ENT)
    ms.nextw(FunB)
    ms.T_ifnotflag("FIN_C")
    ms.nextw(FunC)
    ms.T_nextflag("FIN_C")
    ms.nextw(FunD)
    ms.T_end()
    ms.T_ifnotflag("FIN_E")
    ms.nextw(FunE)
    ms.T_nextflag("FIN_E")
    ms.T_end()
    ms.nextw(FunF)
    ms.T_ifnotflag("FIN_G")
    ms.nextw(FunG)
    ms.T_nextflag("FIN_G")
    ms.T_end()
    ms.T_ifnotflag("FIN_H")
    ms.nextw(FunH)
    ms.T_nextflag("FIN_H")
    ms.T_end()
    ms.T_clearflags()
    ms.exitw(None)
    ms.run("rec", True)
