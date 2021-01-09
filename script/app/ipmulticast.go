package main

import (
	"golang.org/x/tools/go/ssa/interp/testdata/src/os"
	"math"
	"net"
	"strconv"

	//"log"
	"time"

	//"encoding/json"
	"github.com/tendermint/tendermint/libs/json"
	"github.com/dmichael/go-multicast/multicast"
	"github.com/tendermint/tendermint/libs/log"
	"crypto/md5"
)
// 65,535 bytes (8 byte header + 65,527 bytes of data) for a UDP datagram
// set maxbytes to 64000 = 8000 chars
const maxby = 8000

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

			mms := ModelPackageDown(lbr[0])

			for _,m := range mms {
				mod, _ := json.Marshal(m)
				conn.Write(mod)
			}
			//mod, _ := json.Marshal(lbr[0])
			//
			s.logger.Info("Broadcasting...")
			//conn.Write(mod)
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
	s.logger.Info(model.B64model)
	AppendIncomingChannel(*s.LI,ModelStructure{
		From:     model.From,
		Round:    model.Round,
		B64model: model.B64model,
	})

}

func ModelPackageDown(mod ModelStructure) []MulticastModelStructure {
	var mms []MulticastModelStructure

	bymod := []byte(mod.B64model)
	md5sum := md5.Sum([]byte(mod.B64model))

	leng := math.Ceil(float64(len(bymod)) / float64(maxby))

	for i := 1; i <= int(leng); i++ {
		mms = append(mms, MulticastModelStructure{
			From:         os.Getenv("ID"),
			Round:        mod.Round,
			PartB64model: string(bymod[:8000]),
			Md5sum:       md5sum,
			Total:        uint32(leng),
			Index:        uint32(i),
		})

		if i != int(leng) {
			bymod = bymod[8000:]
		}
	}
	return mms
}



func ModelPackageUp(mms []MulticastModelStructure) ModelStructure {

	leng:= mms
	bymod := []byte(mod.B64model)
	md5sum := md5.Sum([]byte(mod.B64model))

	leng := math.Ceil(float64(len(bymod)) / float64(maxby))

	for i := 1; i <= int(leng); i++ {
		mms = append(mms, MulticastModelStructure{
			From:         "",
			Round:        mod.Round,
			PartB64model: string(bymod[:8000]),
			Md5sum:       md5sum,
			Total:        uint32(leng),
			Index:        uint32(i),
		})

		if i != int(leng) {
			bymod = bymod[8000:]
		}
	}
	return mms
}