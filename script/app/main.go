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
	ListBroadcastModel := make(chan LBroadcastModel)
	//threadhold := 5
	//data := dataFile

	// initialize the channel
	go func() {
		ListBaseModel <- LBasemodel{
			lbasemodel: []ModelStructure{},
			MaxRound :	100,
		}
		return
	}()
	go func() {
		ListIncomingModel <- LIncomingModel{
			lincomingmodel: []ModelStructure{},
		}
		return
	}()
	go func() {
		ListBroadcastModel <- LBroadcastModel{
			lbroadcastmodel: []ModelStructure{},
		}
		return
	}()
	//<-ListBaseModel
	//<-ListIncomingModel

	IpfsApp := NewIpfs(logger,"172.168.10.10:5001")
	IpfsApp.InitIpfs()

	addr := "172.168.10.100:62287"
	aggapp := AggRunner(logger,addr,&ListIncomingModel,4, &ListBaseModel)
	aggapp.SetTmpPath("/root/aggmpdels_"+os.Getenv("ID")+".txt")
	aggapp.Connect2Client()

	logger.Info("Node")
	go NodeRunner(logger, configFile, &ListBaseModel, aggapp, IpfsApp)


	trainer := NewTrainer(logger, "172.168.10.5"+os.Getenv("ID")+":62281", &ListBaseModel, &ListBroadcastModel)
	trainer.Connect2Client()
	logger.Info("train")
	go TrainerRunner(*trainer)



	MAddress := "239.0.0.0:9999"
	Multicaster := NewMulticaster(logger, MAddress, &ListIncomingModel, &ListBroadcastModel, IpfsApp)
	go Multicaster.BroadcastingServices()
	go Multicaster.ListeningServices()
	//go func() {
	//	addr := "localhost:62287"
	//	AggRunner(addr)
	//}()
	//logger.Info("dfsdf")


	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c  // wait for get Signal
	//message<- "Done"

	//wg.Wait()
	os.Exit(0)
}

func NodeRunner(logger log.Logger,cfile string, ListBaseModel *chan LBasemodel,agg *AggregatorApplication, ipfs *IpfsApplication){
	app := NewTicketStoreApplication(logger, *ListBaseModel, agg, ipfs)
	node, err := newTendermint(app, cfile)

	if err != nil {
		fmt.Fprintf(os.Stderr, "%v", err)
		os.Exit(2)
	}

	node.Start()
	defer func() {
		fmt.Println("Closing...")
		node.Stop()
		node.Wait()
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
	os.Exit(0)
}

func AggRunner(logger log.Logger, addr string, LI *chan LIncomingModel, thhold uint32, LB *chan LBasemodel) *AggregatorApplication {
	aggregator := NewAggregator(logger, addr, LI, LB, thhold)
	aggregator.SetTmpPath("/tmp/model.txt")

	return aggregator
}

func TrainerRunner (trainer Trainerapplication){
	for{
		trainer.TrainerServices()
		time.Sleep(400 * time.Millisecond)
	}
}

//func MulticastRunner (addr string){
//	for{
//		trainer.TrainerServices()
//		time.Sleep(400 * time.Millisecond)
//	}
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

func  GetBaseChannel(GO chan LBasemodel) LBasemodel {
	msg := <-GO
	go func() {
		GO<- msg
	}()
	return msg
}

func  AppendBaseChannel(GO chan LBasemodel, m ModelStructure) LBasemodel {
	msg := <-GO
	go func() {
		GO<- LBasemodel{
			lbasemodel: append(msg.lbasemodel,m),
			MaxRound :	msg.MaxRound,
		}
	}()
	return msg
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
			append(msg.lincomingmodel,m),
		}
	}()
	return msg
}

func  SetIncomingChannel(GO chan LIncomingModel, m []ModelStructure) {
	go func() {
		GO<- LIncomingModel{
			m,
		}
	}()
}

func  GetBroadcastChannel(GO chan LBroadcastModel) LBroadcastModel {
	msg := <-GO
	go func() {
		GO<- msg
	}()
	return msg
}

func  AppendBroadcastChannel(GO chan LBroadcastModel, m ModelStructure) LBroadcastModel {
	msg := <-GO
	go func() {
		GO<- LBroadcastModel{
			append(msg.lbroadcastmodel,m),
		}
	}()
	return msg
}

func  DeleteBroadcastChannel(GO chan LBroadcastModel)  {
	msg := <-GO
	go func() {
		GO<- LBroadcastModel{
			lbroadcastmodel:msg.lbroadcastmodel[1:],
		}
	}()
}
