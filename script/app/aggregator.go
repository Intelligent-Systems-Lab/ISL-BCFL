package main

import (
	"google.golang.org/grpc"
	//"log"
	//"github.com/orktes/go-torch"
	//"io"
	//b64 "encoding/base64"
	//"github.com/vmihailenco/msgpack"
	//"io/ioutil"
	"os"
	//"os/exec"
	"fmt"

	"github.com/tendermint/tendermint/libs/log"

	"strconv"

	pb "github.com/isl/bcflapp/proto/aggregator"
	"golang.org/x/net/context"
)

type AggregatorApplication struct {
	logger    log.Logger
	Address   string
	tmppath   string
	LI        *chan LIncomingModel
	LB        *chan LBasemodel
	threshold uint32

	client       pb.AggregatorClient
	saveallmodel bool

	ipfsapp *IpfsApplication
}

func NewAggregator(logger log.Logger, addr string, Li *chan LIncomingModel, Lb *chan LBasemodel, td uint32, ipfs *IpfsApplication) *AggregatorApplication {
	return &AggregatorApplication{
		logger:       logger,
		Address:      addr,
		LI:           Li,
		LB:           Lb,
		threshold:    td,
		saveallmodel: true,
		ipfsapp:      ipfs,
	}
}

func (app *AggregatorApplication) SetTmpPath(path string) {
	app.tmppath = path
}

func (app *AggregatorApplication) Aggregate(models []string, nextround int) string {
	blankWriter := ""
	app.logger.Info("Aggregating models, len = " + strconv.Itoa(len(models)))
	//app.logger.Info(models[0])
	for i, s := range models {
		if i != len(models)-1 {
			blankWriter = blankWriter + s + ","
		} else {
			blankWriter = blankWriter + s
		}
	}

	writers(blankWriter, app.tmppath)

	//out, err := exec.Command("python", "agg.py",app.tmppath).Output()
	app.logger.Info("Aggregating...")

	r, err2 := app.client.Aggregate(context.Background(), &pb.AggInfo{
		Round:  int32(nextround),
		Models: blankWriter,
	})
	if err2 != nil {
		app.logger.Error("Unable to aggregate ：" + err2.Error())
		//return
	}

	//if err != nil {
	//	panic(err)
	//}
	//fmt.Printf("%s", out)
	fmt.Println("Aggregate done.")
	return string(r.GetResult())
}

func (app *AggregatorApplication) Connect2Client() {
	app.logger.Info("Agg connect to client... " + app.Address)
	conn, err := grpc.Dial(app.Address, grpc.WithInsecure())

	if err != nil {
		app.logger.Error("Connection faild：%v", err)
		return
	}
	//defer conn.Close()

	c := pb.NewAggregatorClient(conn)

	app.client = c
	//app.logger.Info("Connect success.")
}

func (app *AggregatorApplication) AggServices() interface{} {
	//app.logger.Info("AggServices...")

	//copy//////////////////////////////
	LincomingCopy := GetIncomingChannel(*app.LI).lincomingmodel
	Lb := GetBaseChannel(*app.LB)
	LbaseCopy := Lb.lbasemodel
	app.logger.Info("pass0 " + strconv.Itoa(len(LincomingCopy)))

	// [round 0, round 1, round 2, round 3, round 4]
	//										len()=5
	lastround := len(LbaseCopy) - 1 // if lastround=-1, pass anything.
	if lastround == -1 {
		return nil
	}

	if lastround == int(Lb.MaxRound) { //
		if app.saveallmodel {
			savestring := ""
			for i, m := range LbaseCopy {
				if i == len(LbaseCopy)-1 {
					savestring = savestring + m.B64model
				} else {
					savestring = savestring + m.B64model + ","
				}
			}
			app.logger.Info("Save 100 round models...")
			writers(savestring, "/root/100_round_model_id_"+os.Getenv("ID")+".txt")
		}
		app.saveallmodel = false
		return nil
	}
	////////////////////////////////////

	app.logger.Info("pass1 " + strconv.Itoa(lastround))
	var backModel []ModelStructure
	var filteredModel []ModelStructure
	for _, m := range LincomingCopy {
		if m.Round == uint64(lastround) {
			filteredModel = append(filteredModel, m)
			//app.logger.Info("Appending : "+strconv.Itoa(i))
			app.logger.Info("Appending round : " + strconv.Itoa(lastround))
			//app.logger.Info("Appending model : "+m.B64model)

		} else {
			backModel = append(backModel, m)
		}
	}
	//app.logger.Info("pass2")

	//app.logger.Info("Aggregating...")

	var result string
	if uint32(len(filteredModel)) >= app.threshold {
		app.logger.Info("Aggregating...")
		var fModels []string
		for _, m := range filteredModel {
			fModels = append(fModels, m.B64model)
		}
		app.logger.Info("Aggregating..." + strconv.Itoa(int(filteredModel[0].Round)))
		result = app.Aggregate(fModels, lastround+1)
		app.logger.Info("pass3")
		//SetIncomingChannel(*app.LI, backModel)
	} else {
		app.logger.Info("Waiting for threshold...")
		return nil
	}
	app.logger.Info("pass4")

	//save//////////////////////////////
	LBase_ := GetBaseChannel(*app.LB)
	if Equal(LbaseCopy, LBase_.lbasemodel) {
		app.logger.Info("Add new base model...")
		AppendBaseChannel(*app.LB, ModelStructure{
			Round:    uint64(lastround + 1),
			B64model: result,
		})
		return true
	} else {
		return nil
	}
	////////////////////////////////////
}

func (app *AggregatorApplication) MulticastListening(address string) {

}

func writers(s string, path string) {
	file, err := os.Create(path)
	if err != nil {
		panic(err)
	}

	_, err = file.WriteString(s)
	if err != nil {
		panic(err)
	}
	defer file.Close()
}

func Equal(a, b []ModelStructure) bool {
	if len(a) != len(b) {
		return false
	}
	for i, v := range a {
		if v != b[i] {
			return false
		}
	}
	return true
}
