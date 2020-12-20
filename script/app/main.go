package main

import (
	"flag"
	"fmt"
	"os"

	//"github.com/dgraph-io/badger"

	abciserver "github.com/tendermint/tendermint/abci/server"
	"github.com/tendermint/tendermint/libs/log"
	tmos "github.com/tendermint/tendermint/libs/os"
)

var flagAddress string
var flagAbci string

func init() {
	flag.StringVar(&flagAddress, "address", "tcp://0.0.0.0:26658", "address of application socket")
	flag.StringVar(&flagAbci, "abci", "socket", "either socket or grpc")
}
// func init() {
// 	fmt.Println("Reading from : " + os.Getenv("NODEPATH")+"/config/config.toml")
// 	time.Sleep(1 * time.Second)
// 	flag.StringVar(&configFile, "config", os.Getenv("NODEPATH")+"/config/config.toml", "Path to config.toml")
// }


// func main() {
// 	// db, err := badger.Open(badger.DefaultOptions("/tmp/badger"))
// 	// if err != nil {
// 	// 	fmt.Fprintf(os.Stderr, "failed to open badger db: %v", err)
// 	// 	os.Exit(1)
// 	// }
// 	// defer db.Close()
// 	app := NewTicketStoreApplication()

// 	flag.Parse()

// 	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))

// 	//server := abciserver.NewSocketServer(socketAddr,flagAbci , app)

// 	server, err := abciserver.NewServer(flagAddress, flagAbci, app)

// 	server.SetLogger(logger)
// 	if err := server.Start(); err != nil {
// 		fmt.Fprintf(os.Stderr, "error starting socket server: %v", err)
// 		os.Exit(1)
// 	}
// 	defer server.Stop()

	
// 	//srv, err := server.NewServer(flagAddress, flagAbci, app)
// 	if err != nil {
// 		fmt.Fprintf(os.Stderr, "error starting  server: %v", err)
// 		os.Exit(1)
// 	}
// 	// srv.SetLogger(logger.With("module", "abci-server"))
// 	// if err := srv.Start(); err != nil {
// 	// 	fmt.Fprintf(os.Stderr, "error starting  server: %v", err)
// 	// 	os.Exit(1)
// 	// }

// 	// select {}

// 	c := make(chan os.Signal, 1)
// 	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
// 	<-c
// 	os.Exit(0)
// }


func main()  {
	app := NewTicketStoreApplication()
	logger := log.NewTMLogger(log.NewSyncWriter(os.Stdout))

	// Start the listener
	srv, err := abciserver.NewServer(flagAddress, flagAbci, app)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error starting socket server: %v", err)
		os.Exit(1)
	}
	srv.SetLogger(logger.With("module", "abci-server"))
	if err := srv.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "error starting socket server: %v", err)
		os.Exit(1)
	}
	// Stop upon receiving SIGTERM or CTRL-C.
	tmos.TrapSignal(logger, func() {
		// Cleanup
		if err := srv.Stop(); err != nil {
			logger.Error("Error while stopping server", "err", err)
		}
	})

	// Run forever.
	select {}
}