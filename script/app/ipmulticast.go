package main

import (
	"math/rand"
	"net"
	"strconv"

	//"log"
	"time"
	"github.com/dmichael/go-multicast/multicast"
	//"encoding/json"
	"github.com/tendermint/tendermint/libs/json"
	"github.com/tendermint/tendermint/libs/log"
)
// 65,535 bytes (8 byte header + 65,527 bytes of data) for a UDP datagram
// set maxbytes to 64000 = 8000 chars
const maxby = 8000

type MulticastingServices struct {
	logger log.Logger
	MAddress string "239.0.0.0:9999"

	LI *chan LIncomingModel
	LBR *chan LBroadcastModel

	ipfsapp *IpfsApplication
}

func NewMulticaster(logger log.Logger, address string, Li *chan LIncomingModel, Lbr *chan LBroadcastModel, ipfs *IpfsApplication) *MulticastingServices {
	return &MulticastingServices{
		logger: logger,
		MAddress: address,
		LI: Li,
		LBR: Lbr,
		ipfsapp: ipfs,
	}
}

func (s *MulticastingServices)BroadcastingServices() {
	s.logger.Info("Start BroadcastingServices...")
	conn, err := multicast.NewBroadcaster(s.MAddress)
	if err != nil {
		s.logger.Error(err.Error())
	}

	for {
		lbr := (GetBroadcastChannel(*s.LBR)).lbroadcastmodel
		if  len(lbr) >0 {
			//lbr[0].B64model = s.ipfsapp.AddIpfs(string(lbr[0].B64model))

			mod, _ := json.Marshal(lbr[0])

			s.logger.Info("Broadcasting...")
			time.Sleep(time.Duration(rand.Intn(100))*time.Millisecond)
			conn.Write([]byte(mod))
			DeleteBroadcastChannel(*s.LBR)
			s.logger.Info("Broadcasting done...")
		}else{
			continue
		}
		time.Sleep(500 * time.Millisecond)
	}

	defer conn.Close()
}

func (s *MulticastingServices)ListeningServices() {
	s.logger.Info("Start ListeningServices...")
	s.logger.Info("Listening on "+s.MAddress)
	multicast.Listen(s.MAddress, s.msgHandler)

}

func (s *MulticastingServices)msgHandler(src *net.UDPAddr, n int, b []byte) {
	s.logger.Info("Get message from Multicasting...")

	var model ModelStructure
	err := json.Unmarshal(b[:n], &model)
	if err != nil {
		s.logger.Error(err.Error())
	}
	s.logger.Info("Get message : ")
	s.logger.Info(strconv.Itoa(int(model.Round)))
	//s.logger.Info(model.B64model)
	AppendIncomingChannel(*s.LI,ModelStructure{
		From:     model.From,
		Round:    model.Round,
		//B64model: s.ipfsapp.CatIpfs(model.B64model),
		B64model: model.B64model,
	})

	s.logger.Info("Append multi round : "+strconv.Itoa(int(model.Round))+", len = "+strconv.Itoa(len(GetIncomingChannel(*s.LI).lincomingmodel)))
	s.logger.Info("Get message : Done")
}

