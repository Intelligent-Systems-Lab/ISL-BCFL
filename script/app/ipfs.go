package main

import (
	"bytes"
	"fmt"
	shell "github.com/ipfs/go-ipfs-api"
	"os"

	"github.com/tendermint/tendermint/libs/log"
)

type IpfsApplication struct {
	logger log.Logger
	Address string

	sh *shell.Shell
}

func NewIpfs(logger log.Logger, addr string) *IpfsApplication {
	return &IpfsApplication{
		logger: logger,
		Address: addr,
	}
}

func (s *IpfsApplication)InitIpfs() {
	s.sh = shell.NewShell(s.Address)
}

func (s *IpfsApplication)AddIpfs(intput string) string {
	//rand := "hihihi8787878"
	s.logger.Info("Upload to Ipfs...")
	mhash, err := s.sh.Add(bytes.NewBufferString(intput))
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}

	return mhash
}

func (s *IpfsApplication)CatIpfs(intput string) string {
	s.logger.Info("Download from Ipfs...")
	reader, err := s.sh.Cat(intput)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}
	buf := new(bytes.Buffer)
	buf.ReadFrom(reader)
	catRand := buf.String()

	//fmt.Println(catRand)
	//s.logger.Info("Download from Ipfs...Done")
	return catRand
}