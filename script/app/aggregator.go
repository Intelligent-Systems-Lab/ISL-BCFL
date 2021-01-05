package main

import (
	//"github.com/orktes/go-torch"
	//"io"
	//b64 "encoding/base64"
	//"github.com/vmihailenco/msgpack"
	//"io/ioutil"
	"os"
	"os/exec"
	"fmt"
	"github.com/tendermint/tendermint/libs/log"
)

type AggregatorApplication struct {
	logger log.Logger
	grpcip string
	tmppath string
	LI *chan LIncomingModel
	LB *chan LBasemodel
	threshold uint32
}

func NewAggregator(logger log.Logger, Grpcip string, Li *chan LIncomingModel, Lb *chan LBasemodel, td uint32) *AggregatorApplication {
	return &AggregatorApplication{
		logger: logger,
		grpcip: Grpcip,
		LI: Li,
		LB: Lb,
		threshold: td,
	}
}

func (app *AggregatorApplication) SetTmpPath(path string){
	app.tmppath = path
}

func (app *AggregatorApplication) Aggregate(models []string) string{
	blankWriter := ""

	for i, s := range models{
		if i!=len(models){
			blankWriter = blankWriter + s + ","
		}
		blankWriter = blankWriter+s
	}

	writetxt(blankWriter, app.tmppath)

	out, err := exec.Command("python", "agg.py",app.tmppath).Output()

	if err != nil {
		panic(err)
	}
	//fmt.Printf("%s", out)
	fmt.Println("Aggregate done.")
	return  string(out)
}

func (app *AggregatorApplication)AggServices() interface{}{

	//copy//////////////////////////////
	LincomingCopy := GetIncomingChannel(*app.LI).lincomingmodel
	LbaseCopy := GetBaseChannel(*app.LB).lbasemodel

	// [round 0, round 1, round 2, round 3, round 4]
	//										len()=5
	lastround := len(LbaseCopy)-1 // if lastround=-1, pass anything.
	if lastround == -1{
		return nil
	}
	////////////////////////////////////

	var filteredModel []ModelStructure
	for _,m := range LincomingCopy {
		if m.round == uint64(lastround) {
			filteredModel = append(filteredModel, m)
		}
	}

	var result string
	if uint32(len(filteredModel)) >= app.threshold {
		var filteredModels []string
		for _,m := range filteredModel{
			filteredModels = append(filteredModels, m.b64model)
		}
		result = app.Aggregate(filteredModels)
	}else{
		return nil
	}

	//save//////////////////////////////
	LBase_ := GetBaseChannel(*app.LB)
	if Equal(LbaseCopy, LBase_.lbasemodel){
		app.logger.Info("Aggregating...")
		AppendBaseChannel(*app.LB, ModelStructure{
			round: uint64(lastround+1),
			b64model: result,
		})
		return true
	}else{
		return nil
	}
	////////////////////////////////////
}

func (app *AggregatorApplication)MulticastListening(address string){

}

func writetxt(s string, path string)  {
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