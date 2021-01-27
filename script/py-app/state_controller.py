from messages import AggregateMsg, UpdateMsg


class state:
    def __init__(self, Round, AggWeight, BaseResult, IncomingModel):
        self.Round = Round                  # this round
        self.AggWeight = AggWeight          # last round's incoming-models that aggregate to new base-model
        self.BaseResult = BaseResult        # base-model that aggregate from last round's incoming-models
        self.IncomingModel = IncomingModel  # collection from this round

    def json(self):
        return self.__dict__


class stateController:
    def __init__(self, logger, trainer, aggregator, threshold):
        self.logger = logger
        self.states = []

        self.trainer = trainer
        self.aggregator = aggregator
        self.threshold = threshold

    def txManager(self, tx):
        if tx["Type"] == "aggregation":
            data = AggregateMsg()
            data.set_maxIteration(tx["MaxIteration"])
            data.set_sample(tx["Sample"])
            data.set_round(tx["Param"]["Round"])
            data.set_weight(tx["Param"]["Weight"])
            data.set_result(tx["Param"]["Result"])
            data.set_cid(tx["Param"]["Cid"])
            self.states.append(state(Round=data.get_round(),
                                     AggWeight=data.get_weight(),
                                     BaseResult=data.get_result(),
                                     IncomingModel=data.get_weight()))
            self.trainer.trainRun(data.get_result(), data.get_round())
        elif tx["Type"] == "aggregation":
            data = UpdateMsg()
            data.set_sample(tx["Sample"])
            data.set_round(tx["Param"]["Round"])
            data.set_weight(tx["Param"]["Weight"])
            data.set_cid(tx["Param"]["Cid"])
            if self.states[-1]["Round"] == data.get_round():
                self.states[-1]["IncomingModel"].append(data.get_weight())
                if len(self.states[-1]["IncomingModel"]) >= self.threshold:
                    self.aggregator.aggergateRun(self.states[-1]["IncomingModel"], self.states[-1]["Round"])

    def txChecker(self, tx) -> bool:
        try:
            if tx["Type"] == "aggregation":
                data = AggregateMsg()
                data.set_maxIteration(tx["MaxIteration"])
                data.set_sample(tx["Sample"])
                data.set_round(tx["Param"]["Round"])
                data.set_weight(tx["Param"]["Weight"])
                data.set_result(tx["Param"]["Result"])
                data.set_cid(tx["Param"]["Cid"])
            elif tx["Type"] == "aggregation":
                data = UpdateMsg()
                data.set_sample(tx["Sample"])
                data.set_round(tx["Param"]["Round"])
                data.set_weight(tx["Param"]["Weight"])
                data.set_cid(tx["Param"]["Cid"])
            self.logger.info("TX ok.")
            return True
        except KeyError:
            self.logger.info("TX invalid.")
            return False

