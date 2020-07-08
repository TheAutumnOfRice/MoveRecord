from MoveRecord import moveset
"""
Example 2：
使用wrap函数族进行快速封装：
    moveset.w：封装不需要读写var，或只需要从var中获取固定变量值的函数
    moveset.wv：封装需要读写var的函数（要求函数含有var参数）
    moveset.wif：封装一个判断函数，根据返回bool值跳转到不同的ID

moveset.w(fun:函数,next_id:下一个执行的ID，varmap:变量映射,*args,**kwargs:函数传参）
moveset.wv(fun:函数(需要var参数),next_id:下一个执行的ID，*args,**kwargs:函数传参)
moveset.wif(fun:函数(需要var参数),trueid:fun为真时跳转,falseid:fun为假时跳转)
"""

def Hello():
    print("Hello World!")
    input("按下回车继续...")

def PrintWords(words):
    print(words)
    input("按下回车继续...")
def Plus(a,b):
    print(a,'+',b,'=',a+b)
    input("按下回车继续...")
def SetAB(var):
    var["A"]=int(input("请输入新的A"))
    var["B"]=int(input("请输入新的B"))

def SetPlus(var):
    var["C"]=var["A"]+var["B"]
    print("var中变量C的当前值为：",var["C"])
    input("按下回车继续...")

def MoreThanMAX(var):
    b=var["C"]>var["MAX"]
    print("判别：C比MAX大","成立" if b else "不成立")
    input("按下回车继续...")
    return var["C"]>var["MAX"]

if __name__ == "__main__":
    ms=moveset("example2",use_json=True)
    # 设置初值
    ms.addvar("A",1)
    ms.addvar("B",2)
    ms.addvar("MAX",10)

    # Wrap一个普通的无参函数
    # 创建一个名称为hello的move，执行函数Hello，并且结束后跳转到print
    ms.addmove("hello",ms.w(Hello,"print"),start=True)

    # Wrap一个带参函数
    # 创建一个名称为print的move，执行函数PrintWords，并且结束后跳转到PlusShow
    # 执行PrintWords时，**kwargs格式传入参数HaHa
    ms.addmove("print",ms.w(PrintWords,"PlusShow",words="HaHa"))
    # 创建一个名称为PlusShow的move，执行函数Plus，并且结束后跳转到set
    # 执行Plus时，*args格式传入两个数
    ms.addmove("PlusShow",ms.w(Plus,"set",1,2))

    # WrapVar一个含有var参数的函数
    # 创建一个名称为set的move，执行函数SetAB，并且结束后跳转到plus
    # SetAB含有参数var，需要对var进行独写，因此使用ms.wv
    ms.addmove("set",ms.wv(SetAB,"plus"))

    # ms.w中的varmap参数：变量映射
    # 创建一个名称为plus的move，执行函数Plus，并且结束后跳转到setC
    # Plus函数有两个参数a,b，使用varmap映射，将变量区的A映射为参数a，将B映射为参数b
    ms.addmove("plus",ms.w(Plus,"setC",varmap={"A":"a","B":"b"}))

    # 创建一个名称为setC的move，执行函数SetPlus，并且结束后跳转到check
    # SetPlus含有参数var，需要对变量区进行修改，使用ms.wv
    ms.addmove("setC",ms.wv(SetPlus,"check"))

    # Wrap一个分支函数
    # 创建一个名称为check的move，执行函数MoreThanMAX，该函数需要
    # 如果函数返回为真，则跳转到thank，否则跳转到nope
    ms.addmove("check",ms.wif(MoreThanMAX,"thank","nope"))

    ms.addmove("thank",ms.w(PrintWords,"__exit__",words="谢谢使用！"))
    ms.addmove("nope",ms.w(PrintWords,"set",words="A和B的值没有超过MAX"))

    ms.run("rec",continue_=True)
