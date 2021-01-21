package main

import (
	"github.com/tendermint/tendermint/libs/log"
)

type tx struct {
	logger log.Logger
}


func NewTxHandler(logger log.Logger) *tx {
	return  &tx{
		logger: logger,
	}
}
func (app *tx)SendTxHandler(mtx ModelTx) string {
	return ""
}

func (app *tx)SendTX(mtx ModelTx) string {
	return ""
}

func (app *tx)timeout() string {
	return ""
}