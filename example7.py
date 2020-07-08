from MoveRecord import moveset,moveerr

"""
Example 7：
异常机制处理
自定义moveerr，让moveset捕获并作出相应动作
调用moveset.addcatch来增加一个错误处理机制
moveset.addcatch(code:错误代码,nextid:捕获到code后跳转的ID,savecur:是否暂存当前current，默认为True

使用moveset.seterr(code)来向上层传递错误
如果moveset在run的过程中出现了未知的错误，（非moveset错误）
则该moveset终止运行，并向上raise moveerr(code)

使用特殊ID: "__last__" 来回溯到上一次出错时的current位置
"""

def ReadNum(var):
    print("当前次数：",var["now"],"//",var["total"])
    var["num"]=int(input("请输入一个非负数"))
    if var["num"]<0:
        print("出现负数，报错机制启动")
        raise moveerr("neg")

if __name__ == "__main__":
    ms=moveset("example7",use_json=True)

    ms.addvar("now",0)
    ms.addvar("total",10)

    ms.startw("print('输入非负数游戏')",start_id=0,start=True)
    flag=ms.nextwv(ReadNum)
    ms.nextwv("var['now']+=1")
    ms.endif("var['now']>=var['total']","thank",flag)

    ms.addmove("thank",ms.w("print('谢谢使用!')","__exit__"))
    # 增加一条错误：neg，捕获到该code后，跳转到9999
    ms.addcatch("neg",9999)

    # 从id=9999开始新增一列错误解决机制
    ms.startw("print('出错了！')",start_id=9999)
    ms.nextwv("print('你输入了',var['num'],'可这不是非负数！')")
    # 用__last__跳转到出错前的位置
    ms.endw("print('请重新输入!')",next_id="__last__")

    ms.run("rec",continue_=True)
