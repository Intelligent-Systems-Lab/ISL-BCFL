package main

import (
	"flag"
	"fmt"
	"os"
	"time"
)

var configFile string
var flagAddress string

func init() {
	flag.StringVar(&flagAddress, "grpcip", "localhost:62287", "address of grpc endpoint")
	// flag.StringVar(&flagAbci, "abci", "socket", "either socket or grpc")
	
	flag.StringVar(&configFile, "config", os.Getenv("HOME")+"/.tendermint/config/config.toml", "Path to config.toml")
}

func main()  {
	flag.Parse()
	configFile = configFile + "/config/config.toml"
	fmt.Println("Reading from : " + configFile)
	time.Sleep(1 * time.Second)
}