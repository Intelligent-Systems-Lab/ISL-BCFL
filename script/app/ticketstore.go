package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"

	"github.com/tendermint/tendermint/abci/types"
)

const (
	codeTypeOK            uint32 = 0
	codeTypeEncodingError uint32 = 1
	codeTypeModelError    uint32 = 2
)

var (
	ErrBadRound       = "The round number is not match"
	ErrConflict       = "The model round number has been used"
)

type TicketStoreApplication struct {
	types.BaseApplication
	state State
}

type State struct {
	aggregatedModel Model
	historyModel map[uint64]Snapshot
	height uint64
	round  uint64
	clientsNumber int
	rootHash []byte
}

type Model struct {
	Name string
	weight string
}

type Snapshot struct {
	ready bool
	localModels map[uint64]Model
	update map[uint64]bool
}

//type queryformat struct {
//	aggregatedModel Model
//	historyModel map[uint64]Snapshot
//}

type ModelTx struct {
	Round		uint64	`json:"round"`
	Weight		string `json:"weight"`
	CID			uint64 	`json:"cid"`
	Signature 	string 	`json:"signature"`
}

func NewTicketStoreApplication() *TicketStoreApplication {
	return &TicketStoreApplication{
		state: State{ aggregatedModel: Model{ weight: "" },
					  historyModel: make( map[uint64]Snapshot ),
					  clientsNumber: 4,
					},
		}
}

func (app *TicketStoreApplication) Info(req types.RequestInfo) types.ResponseInfo {
	//var sdata string
	//data := []byte(fmt.Sprintf(`{"round":%v, "model":%v}`, app.state.round, app.state.aggregatedModel.weight))
	//json.Unmarshal(data, &sdata)
	//fmt.Println(sdata)
	return types.ResponseInfo{
		Data:             fmt.Sprintf(`{"round":%v, "model":%v}`, app.state.round, app.state.aggregatedModel.weight),
		LastBlockHeight:  int64(app.state.height),
		LastBlockAppHash: app.state.rootHash,
	}
}

func (app *TicketStoreApplication) DeliverTx(tx types.RequestDeliverTx) types.ResponseDeliverTx {
	var modelTx ModelTx
	err := json.Unmarshal(tx.Tx, &modelTx)

	if err != nil {
		return types.ResponseDeliverTx{
			Code: codeTypeEncodingError,
			Log:  fmt.Sprint(err)}
	}

	nextRound := app.state.round + 1

	if modelTx.Round != nextRound {
		return types.ResponseDeliverTx{
			Code: codeTypeModelError,
			Log: fmt.Sprint(ErrBadRound)}
	}

	cid := modelTx.CID
	if app.state.historyModel[nextRound].ready == false {
		// fmt.Printf("initial struct")
		app.state.historyModel[nextRound] = Snapshot{ ready: true,
													  localModels: make( map[uint64]Model ),
													  update: make( map[uint64]bool )}
	}
	if app.state.historyModel[nextRound].update[cid] {
		return types.ResponseDeliverTx{
			Code: codeTypeModelError,
			Log: fmt.Sprint(ErrConflict)}
	}
	app.state.historyModel[nextRound].update[cid] = true
	app.state.historyModel[nextRound].localModels[cid] = Model{Name: "model_"+strconv.Itoa(int(modelTx.Round)),weight: modelTx.Weight}
	return types.ResponseDeliverTx{Code: codeTypeOK}
}

func (app *TicketStoreApplication) CheckTx(tx types.RequestCheckTx) types.ResponseCheckTx {
	return types.ResponseCheckTx{Code: codeTypeOK}
}

func (app *TicketStoreApplication) Commit() (resp types.ResponseCommit) {

	allClientsUpdate := true
	nextRound := app.state.round + 1

	//fmt.Printf("Update Status: \n")
	//for i := 0 ; i < app.state.clientsNumber; i++ {
	//	fmt.Printf("CID %d: %v\n", i, app.state.historyModel[nextRound].update[uint64(i)])
	//	if app.state.historyModel[nextRound].update[uint64(i)] == false {
	//		allClientsUpdate = false
	//	}
	//}

	//for i := 0 ; i < app.state.clientsNumber; i++ {
	//	if app.state.historyModel[nextRound].update[uint64(i)] == false {
	//		allClientsUpdate = false
	//	}
	//}

	modelsNextRound := app.state.historyModel[nextRound].localModels

	if allClientsUpdate {
		app.state.aggregatedModel = Model{weight: AggregateModel(modelsNextRound, app.state.clientsNumber)}
		app.state.round++
	}

	app.state.height++
	return types.ResponseCommit{Data: []byte{0x00}}
}

func (app *TicketStoreApplication) Query(reqQuery types.RequestQuery) types.ResponseQuery {
	//fmt.Printf("Debug: %v\n", string(reqQuery.Data))
	//fmt.Printf("Debug: %v\n", reqQuery.Path)
	//fmt.Printf("Debug: %v\n", string(reqQuery.Height))
	//fmt.Printf("Debug: %v\n", reqQuery.Prove)
	switch reqQuery.Path {
	case "round":
		return types.ResponseQuery{Value: []byte(fmt.Sprint(app.state.round))}
	case "weight":
		return types.ResponseQuery{Value: []byte(fmt.Sprint(app.state.aggregatedModel.weight))}
	case "clients":
		return types.ResponseQuery{Value: []byte(fmt.Sprint(app.state.clientsNumber))}
	case "broadcast_state":
		return types.ResponseQuery{Value: []byte(fmt.Sprint())}
	default:
		return types.ResponseQuery{Log: fmt.Sprintf("Invalid query path. Expected hash, tx or ticket, got %v", reqQuery.Path)}
	}
}

func AggregateModel(localModels map[uint64]Model, clientsNumber int) (string) {
	out, err := exec.Command("python", "hello.py").Output()
	if err != nil {
		panic(err)
	}
	//fmt.Printf("%s", out)
	//fmt.Println()
	return string(out)
}