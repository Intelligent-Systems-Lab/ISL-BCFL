import json

class BaseMsg:
    __class_cid = "uninitialized"
    __msg_type = "base"
    
    def __init__(self,iter_num=-1,**kwargs):
        self.cid = kwargs["cid"] if "cid" in kwargs else BaseMsg.__class_cid
        self.type = kwargs["type"] if "type" in kwargs else BaseMsg.__msg_type
        self.iter_num = iter_num

    @classmethod
    def get_cid(cls):
        return cls.__class_cid
    
    @classmethod
    def set_cid(cls,value):
        cls.__class_cid = value

    def __str__(self):
        tmp = self.__dict__
        return json.dumps(tmp)
    
    def json_serialize(self):
        return self.__str__()


class UpdateMsg(BaseMsg):
    def __init__(self, **kwargs):
        if not "type" in kwargs:
            kwargs["type"] = "Update"
        else:
            if not kwargs["type"] == "Update":
                raise TypeError(f'TypeError(Update)<={kwargs["type"]}')
        super().__init__(**kwargs)
        self.hash = kwargs["hash"] if "hash" in kwargs else None

    
class AggregateMsg(BaseMsg):
    def __init__(self, **kwargs):
        if not "type" in kwargs:
            kwargs["type"] = "Aggregation"
        else:
            if not kwargs["type"] == "Aggregation":
                raise TypeError(f'TypeError(Aggregation)<={kwargs["type"]}')
        super().__init__(**kwargs)
        self.result = kwargs["result"] if "result" in kwargs else None
        self.update_list = kwargs["update_list"] if "update_list" in kwargs else None


if __name__ == "__main__":
    BaseMsg.set_cid("12345")
    print('BaseMsg.cid=',BaseMsg.get_cid())
    
    a = UpdateMsg(cid="67890",iter_num=10, hash="Testing")
    print(a)
    
    b = UpdateMsg(iter_num=11)
    print(b)
    b.hash = "randomized"
    print(b)
    
    c = AggregateMsg(cid="11223",iter_num=12, update_list=["as","bc","cd"])
    d = c.json_serialize()
    print(d)
    
    e = AggregateMsg(**json.loads(d))
    print(e,e.update_list[0])
    