package main

import (
	"net"
	//"log"
	"time"

	"encoding/json"

	"github.com/dmichael/go-multicast/multicast"
	"github.com/tendermint/tendermint/libs/log"
)


type MulticastingServices struct {
	logger log.Logger
	MAddress string "239.0.0.0:9999"

	LI *chan LIncomingModel
	LBR *chan LBroadcastModel
}

func NewMulticaster(logger log.Logger, address string, Li *chan LIncomingModel, Lbr *chan LBroadcastModel) *MulticastingServices {
	return &MulticastingServices{
		logger: logger,
		MAddress: address,
		LI: Li,
		LBR: Lbr,
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
			mod, _ := json.Marshal(lbr[0])
			s.logger.Info("Broadcasting...")
			conn.Write(mod)
			DeleteBroadcastChannel(*s.LBR)
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
	AppendIncomingChannel(*s.LI,ModelStructure{
		from:     model.from,
		round:    model.round,
		b64model: model.b64model,
	})

}

//func (s *MulticastingServices)ping(addr string) {
//	conn, err := multicast.NewBroadcaster(addr)
//	if err != nil {
//		log.Fatal(err)
//	}
//
//	for {
//		conn.Write([]byte("hello, world\n"))
//		time.Sleep(1 * time.Second)
//	}
//}