package main

import (
	_ "bytes"
	_ "encoding/json"
	_ "fmt"
	abcitypes "github.com/tendermint/tendermint/abci/types"
	"github.com/tendermint/tendermint/libs/log"
	_ "log"
	_ "os"
	_ "strconv"
)

type BcflApplication struct {

}

type ModelTx struct {
	Round     uint64   `json:"round"`
	Weight    []string `json:"weight"`
	Result    string   `json:"result"`
	Cid       uint64   `json:"cid"`
	Signature string   `json:"signature"`
}

func NewBcflApplication(logger log.Logger) *BcflApplication {
	return &BcflApplication{}
}

func (app *BcflApplication) isValid(tx []byte)  uint32{
	return uint32(1)
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
func (app *BcflApplication) CheckTx(req abcitypes.RequestCheckTx) abcitypes.ResponseCheckTx {
	return abcitypes.ResponseCheckTx{}
}

func (app *BcflApplication) BeginBlock(req abcitypes.RequestBeginBlock) abcitypes.ResponseBeginBlock {
	return abcitypes.ResponseBeginBlock{}
}

func (app *BcflApplication) DeliverTx(req abcitypes.RequestDeliverTx) abcitypes.ResponseDeliverTx {
	return abcitypes.ResponseDeliverTx{}
}

func (app *BcflApplication) Commit() abcitypes.ResponseCommit {
	return abcitypes.ResponseCommit{}
}

func (app *BcflApplication) Query(reqQuery abcitypes.RequestQuery)  abcitypes.ResponseQuery {
	return abcitypes.ResponseQuery{}
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

func (app *BcflApplication) Info(req abcitypes.RequestInfo) abcitypes.ResponseInfo {
	return abcitypes.ResponseInfo{}
}
//func (app *BcflApplication) SetOption(req abcitypes.RequestSetOption) abcitypes.ResponseSetOption {
//	return abcitypes.ResponseSetOption{}
//}

func (app *BcflApplication) InitChain(req abcitypes.RequestInitChain) abcitypes.ResponseInitChain {
	return abcitypes.ResponseInitChain{}
}

func (app *BcflApplication) EndBlock(req abcitypes.RequestEndBlock) abcitypes.ResponseEndBlock {
	return abcitypes.ResponseEndBlock{}
}

func (app *BcflApplication) ListSnapshots(snapshots abcitypes.RequestListSnapshots) abcitypes.ResponseListSnapshots {
	panic("implement me")
}

func (app *BcflApplication) OfferSnapshot(snapshot abcitypes.RequestOfferSnapshot) abcitypes.ResponseOfferSnapshot {
	panic("implement me")
}

func (app *BcflApplication) LoadSnapshotChunk(chunk abcitypes.RequestLoadSnapshotChunk) abcitypes.ResponseLoadSnapshotChunk {
	panic("implement me")
}

func (app *BcflApplication) ApplySnapshotChunk(chunk abcitypes.RequestApplySnapshotChunk) abcitypes.ResponseApplySnapshotChunk {
	panic("implement me")
}