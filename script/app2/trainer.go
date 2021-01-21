package main
// Trainer
// https://poweruser.blog/embedding-python-in-go-338c0399f3d5

import (
	"github.com/tendermint/tendermint/libs/log"
)

type trainer struct {
	logger log.Logger
}


func Newtrainer(logger log.Logger) *trainer {
	return  &trainer{
		logger: logger,
	}
}

func (app *trainer)TrainService(Mode string, Round uint32, Model string) string {
	return ""
}

func (app *trainer)training(bastmodel string) string {
	return ""
}