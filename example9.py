from MoveRecord import moveset

"""
2020-07-10更新：__onstart__
进入moveset后，如果定义了__onstart__，则暂存current，先执行__onstart__部分
2020-07-10更新：新增模板 moveset.T_mapstart
用处：在进入moveset后，根据上次的运行位置进行映射跳转
应用场景：
对于某moveset：A->B->C
要求：如果执行B时中断，则下一次从C开始执行；
则可以做mapstart映射B->C
如果检测到进入moveset时，在B处，则跳转到C
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


if __name__ == "__main__":
    ms = moveset("example9")
    ms.startw(FunA, start=True)
    ID_B = ms.nextw(FunB)
    ID_C = ms.exitw(FunC)
    ms.T_mapstart({ID_B: ID_C})
    ms.run("rec")
