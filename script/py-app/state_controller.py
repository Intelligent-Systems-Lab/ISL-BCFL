from messages import AggregateMsg, UpdateMsg, InitMsg
import json


class state:
    def __init__(self, round_, agg_weight, base_result):
        self.round = round_  # this round
        self.agg_weight = agg_weight  # last round's incoming-models that aggregate to new base-model
        self.base_result = base_result  # base-model that aggregate from last round's incoming-models
        self.incoming_model = []  # collection from this round

    def json(self):
        return json.dumps(self.__dict__)


class State_controller:
    def __init__(self, logger, trainer, aggregator, threshold):
        self.logger = logger
        self.states = []

        self.trainer = trainer
        self.aggregator = aggregator
        self.threshold = threshold

    def tx_manager(self, tx):
        # self.logger(str(tx))
        if tx["type"] == "aggregation":
            self.logger.info(">> {}".format(json.dumps(tx)))
            data = AggregateMsg(**tx)
            self.logger.info(">> {}".format(data.json_serialize()))
            if self.get_last_round() == data.get_round():
                self.logger.info("Get round : {} ".format(data.get_round()))
                self.logger.info("round exist, now ay round : {} ".format(self.get_last_round()))
                return

            state_data = state(round_=data.get_round(),
                               agg_weight=data.get_weight(),
                               base_result=data.get_result())
            self.states.append(eval(state_data.json()))
            self.trainer.trainRun(self.get_last_base_model(), self.get_last_round())
            self.logger.info("round ++")

        elif tx["type"] == "update":
            data = UpdateMsg(**tx)
            if self.get_last_round() == data.get_round():
                self.append_incoming_model(data.get_weight())
                self.logger.info("Get incoming model, round: {}, total: {}".format(self.get_last_round(),
                                                                                   len(self.get_incoming_model())))
                if len(self.get_incoming_model()) >= self.threshold:
                    self.aggregator.aggergateRun(self.get_incoming_model(), self.get_last_round())

        elif tx["type"] == "create_task":
            data = InitMsg(**tx)
            state_data = state(round_=0,
                               agg_weight=[],
                               base_result=data.get_weight())
            self.states.append(eval(state_data.json()))
            self.logger.info("round ++")
            self.trainer.trainRun(data.get_weight(), 0)

    def tx_checker(self, tx) -> bool:
        # self.logger.info(tx)
        try:
            if tx["type"] == "aggregation":
                _ = AggregateMsg(**tx)
            elif tx["type"] == "update":
                _ = UpdateMsg(**tx)
            elif tx["type"] == "create_task":
                # self.logger.info(">> create_task")
                _ = InitMsg(**tx)
            self.logger.info("TX valid.")
            return True
        except KeyError:
            self.logger.info("TX invalid.")
            return False

    def get_last_round(self):
        return self.states[-1]["round"]

    def get_last_base_model(self):
        return self.states[-1]["base_result"]

    def append_incoming_model(self, value):
        self.states[-1]["incoming_model"].append(value)

    def get_incoming_model(self):
        return self.states[-1]["incoming_model"]
