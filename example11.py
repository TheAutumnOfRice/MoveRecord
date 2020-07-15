from MoveRecord import moveset

"""
Example 11：
2020-07-11更新： ifflag else end的使用
2020-07-15更新： if （对非临时变量的判断）
处理逻辑：
A->B->
    <IF> mode=1
        -> C->D
    <ELSE> <IF> mode=2
            -> E->F
            <ELSE>
                ->Again Read Mode
            <ENDIF>
    <ENDIF>
                
->G
这种逻辑也可以使用endif,wif实现。flag模板的设计对应了一种向后跳转的需求
在设计wif,endif时，跳转的ID必须事先知道。
使用flag模板，可以自动补全ID
目前尚无法实现elseif
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


if __name__ == "__main__":
    ms = moveset("example11")
    ms.startw(FunA, start=True)
    ms.nextw(FunB)
    RD = ms.nextwv("var['mode']=int(input('请输入mode'))")
    ms.T_if("mode", 1)
    ms.nextw(FunC)
    ms.nextw(FunD)
    ms.T_else()
    ms.T_if("mode", 2)
    ms.nextw(FunE)
    ms.nextw(FunF)
    ms.T_else()
    ms.endw("print('输入错误，请重新输入')", next_id=RD)
    ms.T_end()
    ms.T_end()
    ms.exitw(FunG)
    ms.run("rec")
