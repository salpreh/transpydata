def duckyinterface(target_cls):
    @classmethod
    def check(cls, subcls):
        if cls is not target_cls:
            return super(cls).__subclasshook__(subcls)

        if not hasattr(target_cls, '__abstractmethods__'): return True

        methods = target_cls.__abstractmethods__
        res = True
        for m in methods:
            res &= hasattr(subcls, m) and callable(getattr(subcls, m))

        return res

    setattr(target_cls, '__subclasshook__', check)

    return target_cls

