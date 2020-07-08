from MoveRecord import moveset

"""
Example 5：
上下级moveset的交互
通过__parent__和__moveset__XXX变量实现交互
"""

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

    msb.addmove(0,msb.wv(SayLove,"__exit__"),True)

    msg.addmove(0,msg.wif("var['anger']<10",1,2),True)
    msg.addmove(1,msg.wv(SayNo,"__exit__"))
    msg.addmove(2,msg.wv(SayNoNo,"__exit__"))

    ms=moveset("example5",use_json=True)
    ms.addmove(0,ms.w("print('Say Love!')",1),True)
    ms.addvar("count",0)
    ms.addmove(1,ms.wv("var['count']+=1",2))
    ms.addmove(2,ms.wv('print("第",var["count"],"次尝试")',3))
    ms.addmove(3,ms.wset(msb,4,static=True,initvar={"name":"小明"}))
    ms.addmove(4,ms.wset(msg,5,static=True,initvar={"name":"小红"}))
    ms.addmove(5,ms.wv(ShowAnger,6))
    ms.addmove(6,ms.wif(Again,1,"__exit__"))

    ms.run("rec",continue_=True)




