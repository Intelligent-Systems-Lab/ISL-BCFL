package main

import (
	//"flag"
	"github.com/BCFL/trainer"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	//"log"
	"github.com/tendermint/tendermint/libs/log"
)


type Trainerapplication struct {
	logger log.Logger
	Address string
	LB *chan LBasemodel
	LC *chan LBroadcastModel
	con *grpc.ClientConn
}


func NewTrainer(logger log.Logger, Address string, Lb *chan LBasemodel, Lc *chan LBroadcastModel) *Trainerapplication {
	return &Trainerapplication{
		logger: logger,
		Address: Address,
		LB: Lb,
		LC: Lc,
	}
}

func (app *Trainerapplication)TrainerServices()  {
	//flag.Parse()

	conn, err := grpc.Dial(app.Address, grpc.WithInsecure())
	app.con = conn
	if err != nil {
		app.logger.Error("Connection faild：%v", err)
	}
	defer conn.Close()


	c := trainer.NewTrainerClient(conn)


	gotrain := &trainer.TrainInfo{
		Round:     0,
		BaseModel: "1323",
	}

	r, err := c.Train(context.Background(), gotrain)
	if err != nil {
		app.logger.Error("Unable to run ：%v", err)
	}

	app.logger.Info("result：%d", r.Result)
}