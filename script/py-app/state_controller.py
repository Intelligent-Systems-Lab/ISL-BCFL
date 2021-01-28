from messages import AggregateMsg, UpdateMsg, InitMsg
import json
from utils import Upper_TX_formater, Lower_TX_formater


class state:
    def __init__(self, round_, agg_weight, base_result, incoming_model):
        self.round = round_  # this round
        self.agg_weight = agg_weight  # last round's incoming-models that aggregate to new base-model
        self.base_result = base_result  # base-model that aggregate from last round's incoming-models
        self.incoming_model = incoming_model  # collection from this round

    def json(self):
        return self.__dict__


class State_controller:
    def __init__(self, logger, trainer, aggregator, threshold):
        self.logger = logger
        self.states = []

        self.trainer = trainer
        self.aggregator = aggregator
        self.threshold = threshold

    def tx_manager(self, tx):
        # tx = Lower_TX_formater(tx)
        self.logger(str(tx))
        if tx["type"] == "aggregation":
            data = AggregateMsg(**tx)
            self.states.append(state(round_=data.get_round(),
                                     agg_weight=data.get_weight(),
                                     base_result=data.get_result(),
                                     incoming_model=data.get_weight()))
            self.trainer.trainRun(data.get_result(), data.get_round())
            self.logger.info("round ++")

        elif tx["type"] == "update":
            data = UpdateMsg(**tx)
            if self.get_last_round() == data.get_round():
                self.append_incoming_model(data.get_weight())
                if len(self.get_incoming_model) >= self.threshold:
                    self.aggregator.aggergateRun(self.get_incoming_model, self.get_last_round)

        elif tx["type"] == "create_task":
            data = InitMsg(**tx)
            self.states.append(state(round_=data.get_round(),
                                     agg_weight=[],
                                     base_result=data.get_weight(),
                                     incoming_model=data.get_weight()))

    def tx_checker(self, tx) -> bool:
        # tx = Lower_TX_formater(tx)
        self.logger.info(tx)
        try:
            if tx["type"] == "aggregation":
                _ = AggregateMsg(**tx)
            elif tx["type"] == "update":
                _ = UpdateMsg(**tx)
            elif tx["type"] == "create_task":
                self.logger.info(">> create_task")
                _ = InitMsg(**tx)
            self.logger.info("TX ok.")
            return True
        except KeyError:
            self.logger.info("TX invalid.")
            return False

    def get_last_round(self):
        return self.states[-1]["Round"]

    def append_incoming_model(self, value):
        self.states[-1]["IncomingModel"].append(value)

    def get_incoming_model(self, value):
        return self.states[-1]["IncomingModel"]
