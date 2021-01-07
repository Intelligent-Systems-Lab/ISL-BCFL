package main

import (
	//"flag"

	//"github.com/BCFL/trainer"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	//"log"
	"github.com/tendermint/tendermint/libs/log"
	//"github.com/BCFL/trainer"
	//"../trainer/BCFL/trainer"
	pb "github.com/isl/bcflapp/proto"

)


type Trainerapplication struct {
	logger  log.Logger
	Address string
	LB      *chan LBasemodel
	LC      *chan LBroadcastModel
	client  pb.TrainerClient

	lastround int
}


func NewTrainer(logger log.Logger, Address string, Lb *chan LBasemodel, Lc *chan LBroadcastModel) *Trainerapplication {
	return &Trainerapplication{
		logger: logger,
		Address: Address,
		LB: Lb,
		LC: Lc,

		lastround: -1,
	}
}

func (app *Trainerapplication ) Connect2Client()  {
	app.logger.Info("Connect to client...")
	conn, err := grpc.Dial(app.Address, grpc.WithInsecure())

	if err != nil {
		app.logger.Error("Connection faild：%v", err)
		return
	}
	defer conn.Close()


	c := pb.NewTrainerClient(conn)

	app.client = c
	//app.logger.Info("Connect success.")
}

func (app *Trainerapplication)TrainerServices()  {

	LbaseCopy := GetBaseChannel(*app.LB).lbasemodel
	//LBroadcastCopy := GetBroadcastChannel(*app.LC).lbroadcastmodel

	// [round 0, round 1, round 2, round 3, round 4]
	//										len()=5
	lastround := len(LbaseCopy)-1 // if lastround=-1, pass anything.

	if lastround != (app.lastround+1){
		return
	}

	gotrain := &pb.TrainInfo{
		Round:     int32(LbaseCopy[lastround].round),
		BaseModel: LbaseCopy[lastround].b64model,
	}

	r, err2 := app.client.Train(context.Background(), gotrain)

	if err2 != nil {
		app.logger.Error("Unable to run ：%v", err2)
	}

	AppendBroadcastChannel(*app.LC, ModelStructure{
		//from:     os.Getenv("ID"),
		from:     "",
		round:    uint64(r.Round),
		b64model: r.Result,
	})

	app.logger.Info("Result Round：%d", r.Round)
}