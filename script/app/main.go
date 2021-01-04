package main

// This is aggregator

import (
	"flag"
	"fmt"
	"os"
	"time"

	//"github.com/dgraph-io/badger"

	//abciserver "github.com/tendermint/tendermint/abci/server"
	"github.com/tendermint/tendermint/libs/log"
	//tmos "github.com/tendermint/tendermint/libs/os"

	_ "errors"
	"os/signal"
	"path/filepath"
	"syscall"

	"github.com/spf13/viper"

	abci "github.com/tendermint/tendermint/abci/types"
	cfg "github.com/tendermint/tendermint/config"
	tmflags "github.com/tendermint/tendermint/libs/cli/flags"
	nm "github.com/tendermint/tendermint/node"
	"github.com/tendermint/tendermint/p2p"
	"github.com/tendermint/tendermint/privval"
	"github.com/tendermint/tendermint/proxy"

	//_ trainer "github.com/BCFL/trainer"

)

//var flagAddress string
//var flagAbci string


var configFile string
var dataFile string

func init() {
	//flag.StringVar(&flagAddress, "address", "tcp://0.0.0.0:26658", "address of application socket")
	//flag.StringVar(&flagAbci, "abci", "socket", "either socket or grpc")
	
	flag.StringVar(&configFile, "config", os.Getenv("HOME")+"/.tendermint/config/config.toml", "Path to config.toml")
	flag.StringVar(&dataFile, "data", "", "Path to csv dataset")
}

func main()  {
	flag.Parse()
	configFile = configFile + "/config/config.toml"
	fmt.Println("Reading from : " + configFile)
	time.Sleep(1 * time.Second)

	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))

	// initialize the channel
	// https://ukiahsmith.com/blog/initializing-channels-in-go/
	ListBaseModel := make(chan LBasemodel)
	ListIncomingModel := make(chan LIncomingModel)

	// initialize the channel
	go func() {
		ListBaseModel <- LBasemodel{
			lbasemodel: []ModelStructure{},
		}
		ListIncomingModel <- LIncomingModel{
			lincoming: []ModelStructure{},
		}
		//<-ListBaseModel
		//<-ListIncomingModel
		return
	}()

	 <-ListBaseModel
	//fmt.Println(m)
	//
	//time.Sleep(1 *  time.Second)

	//go NodeRunner(logger, configFile, &ListBaseModel)

	logger.Info("Start AggRunner")
	threshold := 4
	addr := "localhost:62287"
	go AggRunner(logger, addr, &ListIncomingModel, uint32(threshold), &ListBaseModel)
	logger.Info("End AggRunner")

	defer func(){
		close(ListBaseModel)
		close(ListIncomingModel)
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c  // wait for get Signal
	//message<- "Done"

	//wg.Wait()
	os.Exit(0)
}

func NodeRunner(logger log.Logger,configFile string, LB *chan LBasemodel){
	logger.Info("Start node...")

	app := NewTicketStoreApplication(logger, *LB)
	node, err := newTendermint(app, configFile)
	if err != nil {
	fmt.Fprintf(os.Stderr, "%v", err)
	os.Exit(2)
	}
	node.Start()

	defer func() {
		logger.Info("Node closing...")
		node.Stop()
		node.Wait()
	}()

}

func AggRunner(logger log.Logger, addr string, LI *chan LIncomingModel, thhold uint32, LB *chan LBasemodel){
	aggregator := NewAggregator(logger, addr, LI, LB, thhold)
	aggregator.SetTmpPath("/tmp/model.txt")
	go func() {
		pre := <-*LI
		aa:=append(pre.lincoming, ModelStructure{
			round:    0,
			b64model: "45",
		})
		*LI<- LIncomingModel{lincoming: aa}
	}()
	time.Sleep(2*time.Second)

	logger.Info("AggServices running 1")
	mm := GetIncomingChannel(*LI)
	logger.Info("AggServices running 1")
	msg:= mm.lincoming
	logger.Info("AggServices running 1")
	fmt.Println(msg)


	logger.Info("AggServices running 2")
	mm2 := GetIncomingChannel(*LI)
	logger.Info("AggServices running 2")
	msg2:= mm2.lincoming
	logger.Info("AggServices running 2")
	fmt.Println(msg2)

	logger.Info("AggServices running Done")
	//for{
	//	logger.Info("AggServices running...")
	//	//aggregator.AggServices()
	//	mm := <-*LI
	//	msg:= mm.lincoming
	//	fmt.Println(msg)
	//	go func() {
	//		*LI<-mm
	//	}()
	//	//logger.Info("AggServices end running...")
	//	time.Sleep(1 *  time.Millisecond)
	//	logger.Info("AggServices running Done")
	//}
}

//func MulticastRunner(addr string){
//
//}




func newTendermint(app abci.Application, configFile string) (*nm.Node, error) {
	// read config
	config := cfg.DefaultConfig()
	config.RootDir = filepath.Dir(filepath.Dir(configFile))
	viper.SetConfigFile(configFile)
	if err := viper.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("viper failed to read config file: %w", err)
	}
	if err := viper.Unmarshal(config); err != nil {
		return nil, fmt.Errorf("viper failed to unmarshal config: %w", err)
	}
	if err := config.ValidateBasic(); err != nil {
		return nil, fmt.Errorf("config is invalid: %w", err)
	}

	// create logger
	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))
	var err error
	logger, err = tmflags.ParseLogLevel(config.LogLevel, logger, cfg.DefaultLogLevel())
	if err != nil {
		return nil, fmt.Errorf("failed to parse log level: %w", err)
	}

	// read private validator
	pv := privval.LoadFilePV(
		config.PrivValidatorKeyFile(),
		config.PrivValidatorStateFile(),
	)

	// read node key
	nodeKey, err := p2p.LoadNodeKey(config.NodeKeyFile())
	if err != nil {
		return nil, fmt.Errorf("failed to load node's key: %w", err)
	}

	// create node
	node, err := nm.NewNode(
		config,
		pv,
		nodeKey,
		proxy.NewLocalClientCreator(app),
		nm.DefaultGenesisDocProviderFunc(config),
		nm.DefaultDBProvider,
		nm.DefaultMetricsProvider(config.Instrumentation),
		logger)
	if err != nil {
		return nil, fmt.Errorf("failed to create new Tendermint node: %w", err)
	}

	return node, nil
}

func  GetIncomingChannel(GO chan LIncomingModel) LIncomingModel {
	msg := <-GO
	go func() {
		GO<- msg
	}()
	return msg
}

func  AppendIncomingChannel(GO chan LIncomingModel, m ModelStructure) LIncomingModel {
	msg := <-GO
	go func() {
		GO<- LIncomingModel{
			append(msg.lincoming,m),
		}
	}()
	return msg
}