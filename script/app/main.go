package main

import (
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	//"github.com/dgraph-io/badger"

	abciserver "github.com/tendermint/tendermint/abci/server"
	"github.com/tendermint/tendermint/libs/log"
)

var socketAddr string

func init() {
	flag.StringVar(&socketAddr, "socket-addr", "tcp://0.0.0.0:26658", "tcp socket address")
}
// func init() {
// 	fmt.Println("Reading from : " + os.Getenv("NODEPATH")+"/config/config.toml")
// 	time.Sleep(1 * time.Second)
// 	flag.StringVar(&configFile, "config", os.Getenv("NODEPATH")+"/config/config.toml", "Path to config.toml")
// }


func main() {
	// db, err := badger.Open(badger.DefaultOptions("/tmp/badger"))
	// if err != nil {
	// 	fmt.Fprintf(os.Stderr, "failed to open badger db: %v", err)
	// 	os.Exit(1)
	// }
	// defer db.Close()
	app := NewTicketStoreApplication()

	flag.Parse()

	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))

	server := abciserver.NewSocketServer(socketAddr, app)
	server.SetLogger(logger)
	if err := server.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "error starting socket server: %v", err)
		os.Exit(1)
	}
	defer server.Stop()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
	os.Exit(0)
}

// func main() {
// 	// db, err := badger.Open(badger.DefaultOptions("/tmp/badger"))
// 	// if err != nil {
// 	// 	fmt.Fprintf(os.Stderr, "failed to open badger db: %v", err)
// 	// 	os.Exit(1)
// 	// }
// 	// defer db.Close()
// 	app := NewTicketStoreApplication()

// 	flag.Parse()

// 	node, err := newTendermint(app, configFile)
// 	if err != nil {
// 		fmt.Fprintf(os.Stderr, "%v", err)
// 		os.Exit(2)
// 	}

// 	node.Start()
// 	defer func() {
// 		node.Stop()
// 		node.Wait()
// 	}()

// 	c := make(chan os.Signal, 1)
// 	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
// 	<-c
// 	os.Exit(0)
// }

// func newTendermint(app abci.Application, configFile string) (*nm.Node, error) {
// 	// read config
// 	config := cfg.DefaultConfig()
// 	config.RootDir = filepath.Dir(filepath.Dir(configFile))
// 	viper.SetConfigFile(configFile)
// 	if err := viper.ReadInConfig(); err != nil {
// 		return nil, fmt.Errorf("viper failed to read config file: %w", err)
// 	}
// 	if err := viper.Unmarshal(config); err != nil {
// 		return nil, fmt.Errorf("viper failed to unmarshal config: %w", err)
// 	}
// 	if err := config.ValidateBasic(); err != nil {
// 		return nil, fmt.Errorf("config is invalid: %w", err)
// 	}

// 	// create logger
// 	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))
// 	var err error
// 	logger, err = tmflags.ParseLogLevel(config.LogLevel, logger, cfg.DefaultLogLevel())
// 	if err != nil {
// 		return nil, fmt.Errorf("failed to parse log level: %w", err)
// 	}

// 	// read private validator
// 	pv := privval.LoadFilePV(
// 		config.PrivValidatorKeyFile(),
// 		config.PrivValidatorStateFile(),
// 	)

// 	// read node key
// 	nodeKey, err := p2p.LoadNodeKey(config.NodeKeyFile())
// 	if err != nil {
// 		return nil, fmt.Errorf("failed to load node's key: %w", err)
// 	}

// 	// create node
// 	node, err := nm.NewNode(
// 		config,
// 		pv,
// 		nodeKey,
// 		proxy.NewLocalClientCreator(app),
// 		nm.DefaultGenesisDocProviderFunc(config),
// 		nm.DefaultDBProvider,
// 		nm.DefaultMetricsProvider(config.Instrumentation),
// 		logger)
// 	if err != nil {
// 		return nil, fmt.Errorf("failed to create new Tendermint node: %w", err)
// 	}

// 	return node, nil
// }
