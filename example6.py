from MoveRecord import moveset

"""
Example 6：
链式增加，简化调用
如果不强调具体分支的指定，而需要Wrap一系列后一个接着前一个的函数
可以考虑使用start,next,end,exit函数族
使用简化调用函数，则ID为递增的整数。
简化调用函数的返回值为当前Move的ID。

moveset.start函数族: 创建自动序列的开始
不需要指定nextid（自动连到下一个），但是需要指定start_id，表示一串序列的开始
可以设置start参数为True，表示这还是moveset的入口函数
1   moveset.startw
2   moveset.startwv
3   moveset.startset

moveset.next函数族：创建自动序列的第2~n-1个move
不需要指定nextid，其余参数照常。
1   moveset.nextw
2   moveset.nextwv
3   moveset.nextset

moveset.end函数族：创建自动序列的最后一个move
需要指定nextid，表示结束自动序列后，下一步的ID
1   moveset.endw
2   moveset.endwv
3   moveset.endset
4   moveset.endif（此时需要指定trueid和falseid）

moveset.exit函数族：创建自动序列的最后一个move并退出moveset
nextid必为__exit__，但是可以另外指定返回值return_
1   moveset.exitw
2   moveset.exitwv
3   moveset.exitset
"""

# 以example5.py为例进行改写
def SayLove(var):
    print(var["name"],": I Love You!")
    input("按回车继续...")

def SayNo(var):
    print(var["name"],": 但是我拒绝。")
    var["__parent__"]["__moveset__boy"]["anger"]+=2
    var["anger"]+=3
    input("按回车继续...")

def SayNoNo(var):
    count=var["__parent__"]["count"]
    print(var["name"],": 你都说了",count,"遍了！！我！就！拒！绝!")
    var["__parent__"]["__moveset__boy"]["anger"] += 6
    var["anger"] += 4
    input("按回车继续...")

def ShowAnger(var):
    print("男生，气炸了！愤怒值",var["__moveset__boy"]["anger"])
    print("女生，气炸了！愤怒值", var["__moveset__girl"]["anger"])
    input("按回车继续...")

def Again(var):
    a=input("是否继续？[Y]/N")
    if a=="N":
        return False
    else:
        return True

if __name__=="__main__":
    msb=moveset("boy",use_json=True)
    msb.addvar("anger",0)
    msg=moveset("girl",use_json=True)
    msg.addvar("anger", 0)

    msb.addmove(0,msb.wv(SayLove,"__exit__"),True)  # 对于只有一个元素的情况，不能使用自动创建

    msg.addmove(0,msg.wif("var['anger']<10",1,2),True)  # 对于if的情况，只能用于endif，其它需要自己实现

    msg.addmove(1,msg.wv(SayNo,"__exit__"))
    msg.addmove(2,msg.wv(SayNoNo,"__exit__"))

    ms=moveset("example6",use_json=True)
    ms.addvar("count", 0)
    # ms.addmove(0,ms.w("print('Say Love!')",1),True)
    ms.startw("print('Say Love!')",start_id=0,start=True)
    # ms.addmove(1,ms.wv("var['count']+=1",2))
    flag = ms.nextwv("var['count']+=1")  # 标记为flag，用于后面if中可以跳转
    # ms.addmove(2,ms.wv('print("第",var["count"],"次尝试")',3))
    ms.nextwv('print("第",var["count"],"次尝试")')
    # ms.addmove(3,ms.wset(msb,4,static=True,initvar={"name":"小明"}))
    ms.nextset(msb,static=True,initvar={"name":"小明"})
    # ms.addmove(4,ms.wset(msg,5,static=True,initvar={"name":"小红"}))
    ms.nextset(msg,static=True,initvar={"name":"小红"})
    # ms.addmove(5,ms.wv(ShowAnger,6))
    ms.nextwv(ShowAnger)
    # ms.addmove(6,ms.wif(Again,1,"__exit__"))
    ms.endif(Again,flag,"__exit__")  # 以if跳转收尾，这里用到了之前的flag标记，这样不用手动推算ID。
    ms.run("rec",continue_=True)
