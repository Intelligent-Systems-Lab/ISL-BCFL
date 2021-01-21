package main

import (
	"flag"
	"fmt"
	"github.com/tendermint/tendermint/libs/log"
	"os"
	"time"
)

var configFile string
var dataFile string

func init() {
	flag.StringVar(&configFile, "config", os.Getenv("HOME")+"/.tendermint/config/config.toml", "Path to config.toml")
}

func main() {
	flag.Parse()
	configFile = configFile + "/config/config.toml"
	fmt.Println("Reading from : " + configFile)
	time.Sleep(1 * time.Second)

	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))

	trainer := Newtrainer(logger)
	aggregator := Newaggregator(logger)
	nodeapp := NewBcflApplication(logger)

}
