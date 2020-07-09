from MoveRecord import moveset

"""
Example 8:
ret自动设置返回值和nextid跳转

2020-07-09更新：增加自动设置返回值ret的功能
                str2fun增加对None的处理：啥都不做

nextid跳转：
1   对于某一个写好的子moveset，其有一个确定的返回值；
    或者对于某一个MoveFun，其也有一个特定的返回值。
    其返回值被用作下一个执行的ID。
2   通常，nextid需要手动设置，表示不管函数或moveset的返回值如何，总是跳转到nextid中。
    当nextid留空（None）时，则以函数本身返回的结果为下一个跳转的ID。
    但是，这种方法适用性很低，因为不是所有函数在设计时就考虑到了上层的跳转逻辑。
3   解决方法：nextid可以是一个Callable[...,IDType]的函数，当nextid为映射函数时，
    下一个跳转的id为nextid(返回值）。
    则此时在设计函数时，无需考虑到上层逻辑，只需要在上层实现moveset时，对返回值进行判断即可
4   nextid跳转逻辑可以利用wv和wif组合实现，但是这样过于麻烦了。

ret设置
在w,wv,wset以及其自动创建函数族中引入了ret参数
它可以将计算结果返回值赋值给var[ret]
将ret设置为"__return__"可以方便地设置返回值
"""

if __name__ == "__main__":

    # 测试ret参数
    ms1 = moveset("ms1")
    ms1.addvar("A", 4)
    ms1.startwv("var['A']-2", ret="B", start=True)
    ms1.exitwv("var['B']+2", ret="__return__")
    ms2 = moveset("ms2")
    ms2.startset(ms1, ret="A1", initvar={"A": 3}, start=True)
    ms2.nextset(ms1, ret="A2", initvar={"A": 5})
    ms2.exitwv("var['A1']+var['A2']", ret="__return__")

    # 测试nextid跳转映射
    ms = moveset("example8")
    ms.startw("print('两数求和')", start=True)


    def lx(x):
        print(x)
        if x >= 10:
            return 999
        else:
            return 9999


    ms.endset(ms2, next_id=lx)
    ms.startw(None, start_id=999)  # 新更新的None函数：对于一句话函数，这样避免了自己重写的麻烦
    ms.exitw("print('超过10了！')")
    ms.startw(None, start_id=9999)
    ms.exitw("print('没超过10~')")
    ms.run("rec")
