package main
// Aggregator
// https://poweruser.blog/embedding-python-in-go-338c0399f3d5

import (
	"github.com/tendermint/tendermint/libs/log"
)

type aggregator struct {
	inipfs bool
	logger log.Logger
}


func Newaggregator(logger log.Logger) *aggregator {
	return  &aggregator{
		logger: logger,
		inipfs: true,
	}
}

func (app *aggregator)AggService(Mode string, Round uint32, Model []string, Result string) string {
	return ""
}

func (app *aggregator)aggregate(bastmodel []string) string {
	return ""
}