import json
import os
import pickle
from typing import Callable, Any, Optional, Dict, Union, Tuple
from copy import deepcopy

MoveFun = Callable[[Dict], Any]
AnyFun = Union[Callable[..., Any], str]
ConFun = Union[Callable[[Dict], bool], str]
IDType = Union[int, str]
IDFun = Union[Callable[..., IDType], IDType]
FunTuple = Tuple[AnyFun, IDType, Tuple, Dict, Dict, bool, bool]
ErrTuple = Tuple[Any,bool]

class moveerr(Exception):
    """
    行动错误类
    捕获含有特定code的错误，在run外层进行捕获
    根据moveset.catch映射转到对应解决方案分支
    """

    def __init__(self, code, desc=""):
        """
        :param code: 错误代码
        :param desc: （可选）错误描述
        """
        self.code = code
        self.desc = desc


class moveset:
    """
    行动列表类，存放一系列行动列表
    行动函数要求返回值为下一次行动的ID，并且没有输入
    可以用start,next,end,exit函数族自动创建moveset序列
    也可以使用w,wv,wif对函数进行wrap后调用addmove手动创建
    变量区 self.var中的常驻变量：
        __return__ moveset执行完毕后的返回值
        __current__ 当前执行（还没有执行完）的步骤
        __start__ moveset的入口ID
        __parent__ 上层moveset，该变量建议不修改，且会在save和load时主动跳过
        __stack__ 用于捕获异常后，记录上一次current。该变量建议不修改。
    可以使用addvar添加一个变量（或者在运行中使用带有v后缀的wrap函数动态创建）
    """

    def __init__(self, name, addr=None, use_json=True):
        """
        :param name: REC的名称
        :param addr: REC的存放路径（可以不写，在run函数中实现）
        :param use_json: 是否使用json格式存放REC，否则采用pickle格式存放
        """
        self.moves = {}  # 存放一系列MoveFun函数，{IDType:MoveFun->IDType}
        self.var = {}  # 变量区
        self.varinit = {}  # 存放初始化var的信息
        self.catch = {}  # 异常情况处理跳转
        self.errcode = None  # 自身异常代码
        self.parent = None  # 是否有父moveset（被其它moveset调用）
        self.addr = addr
        self.name = name
        self.use_json = use_json  # 警告：json类型只能支持数字和字符串变量！
        self.last_move = None  # 自动创建序列时记录上一次的创建参数

    @staticmethod
    def str2fun(fun):
        """
        把一个str类型的fun用eval或exec函数执行，返回wrap后的函数
        :param fun: 字符串，如果不是字符串则直接返回。
        :return:
        """
        if type(fun) is str:
            funstr = fun

            def str2fun(var: Dict = None):
                try:
                    return eval(funstr)
                except:
                    exec(funstr)

            fun = str2fun
        return fun

    def copy(self):
        """
        复制自身，对变量区深拷贝，moves浅拷贝
        如果var中含有__parent__，则跳过
        """
        t = moveset(self.name, self.addr)
        t.moves = self.moves.copy()
        p = None
        if "__parent__" in self.var:
            p = self.var["__parent__"]
            del self.var["__parent__"]
        t.var = deepcopy(self.var)
        if p is not None:
            self.var["__parent__"] = p
        t.varinit = deepcopy(self.varinit)
        t.parent = self.parent
        t.use_json = self.use_json
        return t

    def setstart(self, id: IDType):
        self.varinit["__start__"] = id
    def seterr(self,code)->None:
        """
        如果该moveset运行时报错，且错误类型不为moveerr
        则该moveset向上报moveerr(code)错误
        设置为None时，向上传递原始错误
        :param code: 错误代码
        """
        self.errcode=code

    def addcatch(self,code,nextid:IDType,savecur=True) -> None:
        """
        新增一个错误解决方案
        :param code: 捕获的moveerr的code
        :param nextid: 捕获到code后跳转的ID
        :param savecur: 是否存储当前位置（存储后，可以使用__last__跳转）
        """
        self.catch[code]=(nextid,savecur)
    def addmove(self, id: IDType, fun: MoveFun, start=False) -> None:
        """
        新增一个行动
        :param id: 行动的ID
        :param fun: 行动函数，传入dict类型的变量var，返回值为下一次行动的ID
        :param start: 是否为第一个执行的行动
        """
        self.moves[id] = fun
        if start:
            self.setstart(id)

    def _autoadd(self, fun: AnyFun, mode, *args, use_var=False, varmap=None, kwargs=None,
                 start_id=None, next_id=None, wrap=True) -> int:
        """
        自动增加一个move，ID递增，后一个连接前一个
        该函数是总处理函数，具体调用可以看更详细的start,next,end,exith函数
        :param fun: 一个待wrap的函数
        :param mode: 增加模式
            0：用于start，开始一系列新的自动递增IDd的move
            1：用于next，第2个至倒数第二个move
            2：用于end和exit，最后一个move，此后连接到其它指定move（或__exit__)
            3：用于exit，指定返回值时。此时传来的fun应该是MoveFun类型，则最后一步不进行wrap。
        :param args: fun函数的参数
        :param use_var: fun函数是否包含var参数以接受变量区self.var
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param start_id: 用于mode 0：初始的ID，必须是一个整数
        :param next_id: 用于mode 2：结束时连接到的ID
        :param wrap: 设置为False则需要进一步wrap，设置为True则自动wrap
        :return: int类型,该步骤的ID
        """
        if kwargs is None:
            kwargs = {}
        last = self.last_move
        fun = self.str2fun(fun)
        if mode == 0:
            assert type(start_id) is int, "自动组建move，必须以int类型的id开始"
            self.last_move = (fun, start_id, args, varmap, kwargs, use_var, wrap)
        if mode >= 1:
            assert last is not None, "必须先start再next！"
            last_fun, last_id, last_args, last_varmap, last_kwargs, last_use_var, last_wrap = last
            assert type(last_id) is int, "自动组建move，上一个id必须是int类型！"
            if last_use_var:
                wpfun = self.wv(last_fun, last_id + 1, *last_args, **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            else:
                wpfun = self.w(last_fun, last_id + 1, *last_args, last_varmap, **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            self.last_move = (fun, last_id + 1, args, varmap, kwargs, use_var, wrap)
        if mode == 2:
            last_fun, last_id, last_args, last_varmap, last_kwargs, last_use_var, last_wrap = self.last_move
            if last_use_var:
                wpfun = self.wv(last_fun, next_id, *last_args, **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            else:
                wpfun = self.w(last_fun, next_id, *last_args, last_varmap, **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            self.last_move = None
        elif mode == 3:
            last_fun, last_id, last_args, last_varmap, last_kwargs, last_use_var, last_wrap = self.last_move
            self.addmove(last_id, last_fun)
            self.last_move = None
        if self.last_move is None:
            return last_id
        else:
            return self.last_move[1]

    def startw(self, fun: AnyFun, *args, start_id: int = 0, varmap=None, kwargs=None, start=False) -> int:
        """
           指定一个编号为start_id的move，此后可以利用next依次连接id递增的move
           不会将变量self.var传入fun中。
           要求start_id必须为整数
           :param fun: 一个待wrap的函数
           :param args: fun函数的参数
           :param varmap: var中变量到fun参数的映射
           :param kwargs: fun函数的参数，字典类型
           :param start_id: 初始的ID，必须是一个整数
           :param start: 是否作为moveset的入口
           :return: int类型,该步骤的ID
           """
        if start:
            self.setstart(start_id)
        return self._autoadd(fun, 0, *args, use_var=False, varmap=varmap, kwargs=kwargs, start_id=start_id)

    def startwv(self, fun: AnyFun, *args, start_id: int = 0, kwargs=None, start=False) -> int:
        """
           指定一个编号为start_id的move，此后可以利用next依次连接id递增的move
           要求fun含有参数var以接受变量区self.var
           要求start_id必须为整数
           :param fun: 一个待wrap的函数
           :param args: fun函数的参数
           :param kwargs: fun函数的参数，字典类型
           :param start_id: 初始的ID，必须是一个整数
            :param start: 是否作为moveset的入口
           :return: int类型,该步骤的ID
           """
        if start:
            self.setstart(start_id)
        return self._autoadd(fun, 0, *args, use_var=True, kwargs=kwargs, start_id=start_id)

    def startset(self, ms, start_id: int = 0, start=False, static=False, initvar: Optional[Dict] = None) -> int:
        """
        wrap个moveset，并作为start。
        :param ms: moveset类
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        :param start_id: 初始的ID，必须是一个整数
        :param start: 是否作为moveset的入口
        :return: int类型,该步骤的ID
        """
        fset = self.wset(ms, 0, static, initvar)
        return self.startwv(fset, start_id=start_id, start=start)

    def nextw(self, fun: AnyFun, *args, varmap=None, kwargs=None) -> int:
        """
            wrap一个fun，并将它与上一次start或next的fun连接。
            不会将变量self.var传入fun中。
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param varmap: var中变量到fun参数的映射
         :param kwargs: fun函数的参数，字典类型
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 1, *args, use_var=False, varmap=varmap, kwargs=kwargs)

    def nextwv(self, fun: AnyFun, *args, kwargs=None) -> int:
        """
            wrap一个fun，并将它与上一次start或next的fun连接。
            要求fun含有参数var以接受变量区self.var
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param kwargs: fun函数的参数，字典类型
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 1, *args, use_var=True, kwargs=kwargs)

    def nextset(self, ms, static=False, initvar: Optional[Dict] = None) -> int:
        """
        wrap个moveset，并连接到next。
        :param ms: moveset类
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        :return: int类型,该步骤的ID
        """
        fset = self.wset(ms, 0, static, initvar)
        return self.nextwv(fset)

    def endw(self, fun: AnyFun, *args, next_id: Optional[IDFun] = None, varmap=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个自动创建流程，新fun将指向next_id处
         不会将变量self.var传入fun中。
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param next_id: 结束时连接到的ID
        :return: int类型,该步骤的ID
        """
        return self._autoadd(fun, 2, *args, next_id=next_id, kwargs=kwargs, varmap=varmap, use_var=False)

    def endwv(self, fun: AnyFun, *args, next_id: Optional[IDFun] = None, kwargs=None) -> int:
        """
          wrap一个fun，并将它与上一次start或next的fun连接。
          结束整个自动创建流程，新fun将指向next_id处
          要求fun含有参数var以接受变量区self.var
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param kwargs: fun函数的参数，字典类型
         :param next_id: 结束时连接到的ID
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 2, *args, next_id=next_id, kwargs=kwargs, use_var=True)

    def endset(self, ms, next_id: Optional[IDType] = None, static=False, initvar: Optional[Dict] = None):
        """
          wrap个moveset，并连接到end。
          :param ms: moveset类
          :param static: 如果设置为True，在子moveset结束后，其变量区不删除
          :param initvar: 补充修改原movesetd的初值
          :param next_id: 结束时连接到的ID
          :return: int类型,该步骤的ID
          """
        fset = self.wset(ms, 0, static, initvar)
        return self.endwv(fset, next_id=next_id)

    def endif(self, con: ConFun, trueid: IDType, falseid: IDType) -> int:
        """
        结束一个自动添加系列，按照con条件转到其它分支
        :param con: 条件函数，参数为var字典，返回true或false
        :param trueid: 返回为true时进行的分支
        :param falseid: 返回为false时进行的分支:
        :return: int类型,该步骤的ID
        """
        iffun = self.wif(con, trueid, falseid)
        return self._autoadd(iffun, mode=2, use_var=True, wrap=False)

    def exitw(self, fun: AnyFun, *args, return_=None, varmap=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个moveset，并且返回return_（如果设置为None，则不会特别设置返回值）
         不会将变量self.var传入fun中。
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param return_: 返回值，设置为None时，不会特别设置返回值
        :return:int类型,该步骤的ID
        """
        if return_ is None:
            return self._autoadd(fun, 2, *args, next_id="__exit__", varmap=varmap, kwargs=kwargs, use_var=False)
        else:
            def f(var: Dict) -> IDType:
                fun(*args, **kwargs)
                var["__return__"] = return_
                return "__exit__"

            return self._autoadd(f, 3)

    def exitwv(self, fun: AnyFun, *args, return_=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个moveset，并且返回return_（如果设置为None，则不会特别设置返回值）
        要求fun含有参数var以接受变量区self.var
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param kwargs: fun函数的参数，字典类型
        :param return_: 返回值，设置为None时，不会特别设置返回值
        :return: int类型,该步骤的ID
        """
        if return_ is None:
            return self._autoadd(fun, 2, *args, next_id="__exit__", kwargs=kwargs, use_var=True)
        else:
            def f(var: Dict) -> IDType:
                fun(*args, **kwargs, var=var)
                var["__return__"] = return_
                return "__exit__"

            return self._autoadd(f, 3)

    def exitset(self, ms, return_=None, static=False, initvar: Optional[Dict] = None) -> int:
        """
          wrap个moveset，并连接到end。
          :param ms: moveset类
          :param static: 如果设置为True，在子moveset结束后，其变量区不删除
          :param initvar: 补充修改原movesetd的初值
          :param return_: 返回值，设置为None时，不会特别设置返回值
          :return: int类型,该步骤的ID
          """
        fset = self.wset(ms, 0, static, initvar)
        return self.exitwv(fset, return_=return_)

    def addvar(self, varname, init=None) -> None:
        """
        新增一个变量
        :param varname: 变量的名称
        :param init: 变量的初值
        """
        self.varinit[varname] = init

    def setdefault(self):
        """
        初始化变量区
        """
        for i, j in self.varinit.items():
            self.var.setdefault(i, j)
        self.var.setdefault("__current__", None)
        self.var.setdefault("__return__", None)
        self.var.setdefault("__start__", None)

    @staticmethod
    def w(fun: AnyFun, nextid: Optional[IDFun] = None, *args, varmap: Optional[Dict] = None, **kwargs) -> MoveFun:
        """
        wrap一个普通函数为行动函数，并且该函数不会使用到变量var
        :param fun: 需要wrap的函数
        :param varmap: 指定某些var中变量到fun参数的映射
        :param nextid: 下一个行动的ID，若设置为None，则以fun的返回值为准；也可以为映射函数
        :param args: fun函数的参数
        :param kwargs: fun函数的参数
        :return: wrap后的函数
        """
        fun = moveset.str2fun(fun)
        if varmap is None:
            varmap = {}

        def f(var: Dict):
            for i, j in varmap.items():
                kwargs[j] = var[i]
            a = fun(*args, **kwargs)
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    @staticmethod
    def wv(fun: AnyFun, nextid: Optional[IDFun] = None, *args, **kwargs) -> MoveFun:
        """
        wrap一个普通函数为行动函数，该函数必须携带var参数来接受变量区
        :param fun: 需要wrap的函数
        :param nextid: 下一个行动的ID，若设置为None，则以fun的返回值为准
        :param args: fun函数的参数
        :param kwargs: fun函数的参数
        :return: wrap后的函数
        """
        fun = moveset.str2fun(fun)

        def f(var: Dict):
            a = fun(*args, **kwargs, var=var)
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    @staticmethod
    def wif(con: ConFun, trueid: IDType, falseid: IDType) -> MoveFun:
        """
        wrap一个分支跳转函数
        :param con: 条件函数，参数为var字典，返回true或false
        :param trueid: 返回为true时进行的分支
        :param falseid: 返回为false时进行的分支
        :return: wrap后的函数
        """
        con = moveset.str2fun(con)

        def f(var: Dict):
            if con(var):
                return trueid
            else:
                return falseid

        return f

    def wset(self, ms, nextid: Optional[IDFun] = None, static=False, initvar: Optional[Dict] = None) -> MoveFun:
        """
        wrap个moveset
        :param ms: moveset类
        :param nextid: 下一个行动的ID，若设置为None，则以ms的的返回值为准
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        """
        sub_name = "__moveset__%s" % ms.name
        ms = ms.copy()
        if initvar is None:
            initvar = {}

        def f(var: Dict):
            var.setdefault(sub_name, {})
            var[sub_name].update(initvar)
            try:
                a = ms.run(var=var[sub_name], continue_=True, parent=self)
            finally:
                if not static:
                    del var[sub_name]
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    def _savestate(self):
        if not os.path.isdir(self.addr):
            os.makedirs(self.addr)
        path = "%s\\%s.rec" % (self.addr, self.name)
        if not self.use_json:
            mode = "wb"
        else:
            mode = "w"
        file = open(path, mode)
        if self.use_json:
            json.dump(self.var, file, indent=1)
        else:
            pickle.dump(self.var, file)
        file.close()

    def _loadstate(self):
        path = "%s\\%s.rec" % (self.addr, self.name)
        if not os.path.exists(path):
            return
        if not self.use_json:
            mode = "rb"
        else:
            mode = "r"
        file = open(path, mode)
        self.var.clear()
        if self.use_json:
            self.var.update(json.load(file))
        else:
            self.var.update(pickle.load(file))
        file.close()

    def savestate(self):
        """
        保存变量区的内容
        跳过全部的__parent__
        """
        p = self
        if p.parent is not None:
            del p.var["__parent__"]
            p.parent.savestate()
            p.var["__parent__"] = p.parent.var
        else:
            p._savestate()

    def loadstate(self):
        """
        从文件加载变量区的内容
        """
        p = self
        while p.parent is not None:
            p = p.parent
        p._loadstate()

    def run(self, addr=None, continue_=True, var=None, start: Optional[IDType] = None, parent=None):
        """
        启动moveset
        :param var: 指定变量区域的（某些）值，其余使用初值
        :param continue_: 是否从上一次中断处继续
        :param start: 指定开始ID
        :param parent: moveset类型，指定父亲
        :param addr: 设置存储路径位置
        :return: moveset的返回值（self.var["__return__"]）
        """
        if var is not None:
            self.var = var
        self.setdefault()
        self.parent = parent
        if addr is not None:
            self.addr = addr
        cur = None
        if continue_:
            if self.parent is None:
                self.loadstate()
            cur = self.var["__current__"]
        if cur is None:
            cur = start if start is not None else self.var["__start__"]
        if self.parent is not None:
            self.var["__parent__"] = self.parent.var
        while cur in self.moves or cur == "__last__":
            if cur=="__last__":
                # 跳转到上一次保存的位置
                if "__stack__" in self.var:
                    cur = self.var["__stack__"][-1]
                    del self.var["__stack__"][-1]
                    if len(self.var["__stack__"])==0:
                        del self.var["__stack__"]
                else:
                    cur = "__exit__"
                    print("Current Stack Empty!")
                    break
            self.var["__current__"] = cur
            self.savestate()
            try:
                cur = self.moves[cur](self.var)
            except moveerr as me:
                if me.code in self.catch:
                    # 暂存当前cur并跳转
                    nextid,savecur=self.catch[me.code]
                    if savecur:
                        self.var.setdefault("__stack__",[])
                        self.var["__stack__"]+=[cur]
                    cur = nextid
                else:
                    raise me
            except Exception as e:
                if "__parent__" in self.var:
                    del self.var["__parent__"]
                if type(e) is not moveerr and self.errcode is not None:
                    raise moveerr(self.errcode,desc=self.name)
                else:
                    raise e

        self.var["__current__"] = None
        self.savestate()
        if cur != "__exit__":
            print("Unknown Moveset:", cur)
        if "__parent__" in self.var:
            del self.var["__parent__"]
        return self.var["__return__"]