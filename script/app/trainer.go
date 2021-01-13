package main

import (
	//"flag"

	//"github.com/BCFL/trainer"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"strconv"

	//"log"
	"github.com/tendermint/tendermint/libs/log"
	//"github.com/BCFL/trainer"
	//"../trainer/BCFL/trainer"
	pb "github.com/isl/bcflapp/proto/trainer"
)


type Trainerapplication struct {
	logger  log.Logger
	Address string
	LB      *chan LBasemodel
	LC      *chan LBroadcastModel
	client  pb.TrainerClient

	lastround int

	ipfsapp *IpfsApplication
}


func NewTrainer(logger log.Logger, Address string, Lb *chan LBasemodel, Lc *chan LBroadcastModel, ipfs *IpfsApplication) *Trainerapplication {
	return &Trainerapplication{
		logger: logger,
		Address: Address,
		LB: Lb,
		LC: Lc,

		lastround: -1,
		ipfsapp:ipfs,
	}
}

func (app *Trainerapplication ) Connect2Client()  {
	app.logger.Info("Trainer connect to client... "+app.Address)
	conn, err := grpc.Dial(app.Address, grpc.WithInsecure())

	if err != nil {
		app.logger.Error("Connection faild：%v", err)
		return
	}
	//defer conn.Close()


	c := pb.NewTrainerClient(conn)

	app.client = c
	//app.logger.Info("Connect success.")
}

func (app *Trainerapplication)TrainerServices()  {
	//app.logger.Info("Trainer alive")
	LbaseCopy := GetBaseChannel(*app.LB).lbasemodel
	//LBroadcastCopy := GetBroadcastChannel(*app.LC).lbroadcastmodel

	// [round 0, round 1, round 2, round 3, round 4]
	//										len()=5
	lastround := len(LbaseCopy)-1 // if lastround=-1, pass anything.

	if lastround != (app.lastround+1){
		return
	}
	//app.logger.Info("You want training ?")
	app.logger.Info("Training round : "+strconv.Itoa(int(LbaseCopy[lastround].Round)))
	//app.logger.Info(LbaseCopy[lastround].b64model)
	//return


	r, err2 := app.client.Train(context.Background(), &pb.TrainInfo{
		Round:     int32(LbaseCopy[lastround].Round),
		BaseModel: app.ipfsapp.CatIpfs(LbaseCopy[lastround].B64model),
	})
	if err2 != nil {
		app.logger.Error("Unable to run ：",err2)
		return
	}

	AppendBroadcastChannel(*app.LC, ModelStructure{
		//from:     os.Getenv("ID"),
		Round:    uint64(r.GetRound()),
		B64model: r.GetResult(),
	})
	app.lastround = lastround

	//app.logger.Info("Result Round："+ strconv.Itoa(int(LbaseCopy[lastround].Round)))
	//app.logger.Info("Result Round："+ strconv.Itoa(int(r.Round)))

}