from messages import AggregateMsg, UpdateMsg, InitMsg
import json, os


class state:
    def __init__(self, round_, agg_weight, base_result, selected_aggregator=""):
        self.round = round_  # this round
        self.agg_weight = agg_weight  # last round's incoming-models that aggregate to new base-model
        self.base_result = base_result  # base-model that aggregate from last round's incoming-models
        self.incoming_model = []  # collection from this round
        self.selection_nonce = 0
        self.aggregation_timeout = 3 # 3 block
        self.aggregation_timeout_count = 0
        self.number_of_validator = 4
        self.aggregator_id = -1

    def json(self):
        return json.dumps(self.__dict__)


class State_controller:
    def __init__(self, logger, trainer, aggregator, threshold):
        self.logger = logger
        self.states = []

        self.trainer = trainer
        self.aggregator = aggregator
        self.threshold = threshold

        self.max_iteration = 50
        self.is_saved = False

        self.aggregation_lock = False

    def aggregate_pipe(self, tx):
        data = AggregateMsg(**tx)
        if self.get_last_round() == data.get_round():
            self.logger.info("Get round : {} ".format(data.get_round()))
            self.logger.info("round exist, now at round : {} ".format(self.get_last_round()))
            return
        if  not str(self.get_last_state()["aggregator_id"]) == str(data.get_cid()):
            self.logger.info("Invalid aggregate cid, the aggregator id should be {}".format(self.get_last_state()["aggregator_id"]))
            return

        state_data = state(round_=data.get_round(),
                           agg_weight=data.get_weight(),
                           base_result=data.get_result())
        self.states.append(eval(state_data.json()))
        self.aggregation_lock = False

    def update_pipe(self, tx):
        data = UpdateMsg(**tx)
        # data.get_round
        if self.aggregation_lock:
            return
        if self.get_last_round() == data.get_round():
            self.append_incoming_model({"model":data.get_weight(), "cid": data.get_cid()})
            self.logger.info("Get incoming model, round: {}, total: {}".format(self.get_last_round(),
                                                                               len(self.get_incoming_model())))

    def create_task_pipe(self, tx):
        data = InitMsg(**tx)
        state_data = state(round_=0,
                           agg_weight=[],
                           base_result=data.get_weight())
        self.states.append(eval(state_data.json()))
        self.trainer.train_run(data.get_weight(), 0)
        self.max_iteration = data.get_max_iteration()
        self.logger.info("Max iteration: {}".format(data.get_max_iteration()))

    def pipes(self, type_):
        dis = {"create_task": self.create_task_pipe, "aggregation": self.aggregate_pipe, "update": self.update_pipe}
        return dis[type_]

    #######################################################
    def tx_manager(self, tx):
        if not self.task_end_check():
            return

        if tx == None and self.aggregation_lock: # Endblock : tx = None 
            self.get_last_state()["aggregation_timeout_count"] += 1
            if self.get_last_state()["aggregation_timeout_count"] >= self.get_last_state()["aggregation_timeout"]:
                self.get_last_state()["aggregation_timeout_count"] = 0
                self.get_last_state()["selection_nonce"] += 1
                self.aggregator.aggergate_manager(txmanager=self, tx={"type": "aggregate_again"})
            return
        if tx == None:
            return
        self.pipes(tx["type"])(tx)

        self.trainer.train_manager(txmanager=self, tx=tx)
        self.aggregator.aggergate_manager(txmanager=self, tx=tx)

    #######################################################
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
        try:
            round_ = self.states[-1]["round"]  # init state have no element
        except:
            round_ = -1
        return round_

    def get_last_base_model(self):
        try:
            state_ = self.states[-1]["base_result"]  # init state have no element
        except:
            state_ = ""
        return state_

    def append_incoming_model(self, value):
        self.states[-1]["incoming_model"].append(value)

    def get_incoming_model(self):
        return [i["model"] for i in self.states[-1]["incoming_model"]]

    def get_last_nonce(self):
        try:
            return self.states[-1]["selection_nonce"]
        except:
            return 0

    def set_last_nonce(self, value):
        try:
            self.states[-1]["selection_nonce"] = value
        except:
            pass

    def get_last_state(self):
        try:
            return self.states[-1]
        except:
            return 0

    def task_end_check(self) -> bool:
        # self.logger.info(">>>>>>>> {}".format(len(self.states)))
        # self.logger.info(">>>>>>>> {}".format(self.get_last_round()))
        if len(self.states) >= self.max_iteration and self.get_last_round() >= self.max_iteration - 1:
            if not self.is_saved:
                result = {"data": self.states}
                with open('/root/py-app/{}_round_result_{}.json'.format(self.max_iteration, os.getenv("ID")), 'w') as outfile:
                    json.dump(result, outfile, indent=4)
                self.logger.info("Save to file....")
            self.is_saved = True
            return False
        else:
            return True
