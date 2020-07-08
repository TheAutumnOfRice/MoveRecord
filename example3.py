from MoveRecord import moveset
"""
Example 3：
使用字符串来表示函数
对于简单的操作进行简化

用字符串表示的函数，首先会尝试使用eval执行函数，此时函数返回值为eval后的值；
如果eval无法执行该函数，则使用exec执行,此时该函数返回值为None
"""

def SetReturn(var):
    s=1
    for i in range(var["A"]):
        s=s*2
    var["__return__"]=s
if __name__=="__main__":
    ms = moveset("example3",use_json=True)

    # fun参数可以使用字符串代替
    # 对于简单的函数，无需单独写一个def了
    # 注：此时不能够使用varmap参数，因为字符串函数只有一个参数var
    ms.addmove(0,ms.w('print("Hello World!")',1),True)

    # 使用ms.wv的Wrap时，自带var参数，可以直接使用
    ms.addmove(1,ms.wv('var["A"]=int(input("请设置A的值"))',2))

    # 使用ms.wif的Wrap时，可以直接写逻辑表达式
    ms.addmove(2,ms.wif('0<var["A"]<10',3,4))

    # 对于比较复杂的函数，不建议单独拆开
    # 函数拆的越散，程序运行效率越低，一般尽可能地以一个必要的整体为move单位
    ms.addmove(3,ms.wv(SetReturn,"__exit__"))

    ms.addmove(4,ms.wv('print("值必须在0~10之间，而不是",var["A"])',1))

    rt=ms.run("rec",continue_=True)

    # 运行结束后，可以从var字典中取出某些值
    print("2的",ms.var["A"],"次方为",rt)