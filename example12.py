from MoveRecord import moveset

"""
Example 12：
强制重新运行与子moveset的关系
对于结构
A->
 sub moveset{B->C->D->}
->E
如果在C处中断，而上层moveset设置了强制从A
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


sms = moveset("sub")
sms.startw(FunB, start=True)
sms.nextw(FunC)
sms.exitw(FunD)
ms = moveset("Example12")
ENT = ms.startw(FunA)
ms.nextset(sms)
ms.exitw(FunE)
ms.T_forcestart(ENT)
ms.run("rec")
