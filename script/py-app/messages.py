import json


class BaseMsg:
    __msg_Type = ""
    __msg_MaxIteration = 0
    __msg_Sample = 1

    def __init__(self, **kwargs):
        self.Type = kwargs["Type"] if "Type" in kwargs else BaseMsg.__msg_Type
        self.MaxIteration = kwargs["MaxIteration"] if "MaxIteration" in kwargs else BaseMsg.__msg_MaxIteration
        self.Sample = kwargs["Sample"] if "Sample" in kwargs else BaseMsg.__msg_Sample

    def get_type(self):
        return self.Type

    def get_maxIteration(self):
        return self.MaxIteration

    def get_sample(self):
        return self.Sample

    def set_type(self, value):
        self.Type = value

    def set_maxIteration(self, value):
        self.MaxIteration = value

    def set_sample(self, value):
        self.Sample = value

    # def __str__(self):
    #     tmp = self.__dict__
    #     return json.dumps(tmp)
    #
    # def json_serialize(self):
    #     return self.__str__()


class UpdateMsg(BaseMsg):
    __msg_Round = 0
    __msg_Weight = ""
    __msg_Cid = 0

    def __init__(self, **kwargs):
        if not "Type" in kwargs:
            kwargs["Type"] = "update"
        else:
            if not kwargs["Type"] == "update":
                raise TypeError(f'TypeError(update)<={kwargs["Type"]}')
        super().__init__(**kwargs)
        self.Round = kwargs["Round"] if "Round" in kwargs else UpdateMsg.__msg_Round
        self.Weight = kwargs["Weight"] if "Weight" in kwargs else UpdateMsg.__msg_Weight
        self.Cid = kwargs["Cid"] if "Cid" in kwargs else UpdateMsg.__msg_Cid

    def get_round(self):
        return self.Round

    def get_weight(self):
        return self.Weight

    def get_cid(self):
        return self.Cid

    def set_round(self, value):
        self.Round = value

    def set_weight(self, value):
        self.Weight = value

    def set_cid(self, value):
        self.Cid = value

    def __str__(self):
        param = {}
        data = self.__dict__
        param["Round"] = data.pop("Round")
        param["Weight"] = data.pop("Weight")
        param["Cid"] = data.pop("Cid")
        data["Param"] = param
        return data

    def json_serialize(self):
        return json.dumps(self.__str__())

    def json(self):
        return self.__str__()


class AggregateMsg(BaseMsg):
    __msg_Round = 0
    __msg_Weight = []
    __msg_Result = ""
    __msg_Cid = 0

    def __init__(self, **kwargs):
        if not "Type" in kwargs:
            kwargs["Type"] = "aggregation"
        else:
            if not kwargs["Type"] == "aggregation":
                raise TypeError(f'TypeError(aggregation)<={kwargs["Type"]}')

        super().__init__(**kwargs)
        self.Round = kwargs["Round"] if "Round" in kwargs else AggregateMsg.__msg_Round
        self.Weight = kwargs["Weight"] if "Weight" in kwargs else AggregateMsg.__msg_Weight
        self.Result = kwargs["Weight"] if "Weight" in kwargs else AggregateMsg.__msg_Result
        self.Cid = kwargs["Cid"] if "Cid" in kwargs else AggregateMsg.__msg_Cid

    def get_round(self):
        return self.Round

    def get_weight(self):
        return self.Weight

    def get_result(self):
        return self.Result

    def get_cid(self):
        return self.Cid

    def set_round(self, value):
        self.Round = value

    def set_weight(self, value):
        self.Weight = value

    def set_result(self, value):
        self.Result = value

    def set_cid(self, value):
        self.Cid = value

    def __str__(self):
        param = {}
        data = self.__dict__
        param["Round"] = data.pop("Round")
        param["Weight"] = data.pop("Weight")
        param["Result"] = data.pop("Result")
        param["Cid"] = data.pop("Cid")
        data["Param"] = param
        return data

    def json_serialize(self):
        return json.dumps(self.__str__())

    def json(self):
        return self.__str__()


if __name__ == "__main__":
    a = UpdateMsg()
    print(a.json_serialize())

    b = AggregateMsg()
    b.set_sample(1)
    b.set_maxIteration(100)
    b.set_round(23)
    b.set_weight(["abc", "def"])
    b.set_result("123")
    print(b.json_serialize())
    # >  {"Type": "aggregation", "MaxIteration": 100, "Sample": 1, "Param": {"Round": 23, "Weight": ["abc", "def"],
    #     "Result": "123", "Cid": 0}}
