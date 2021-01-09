package main

//import (
//	_ "fmt"
//	//"github.com/TomorrowWu/golang-algorithms/data-structures/queue"
//)

type LBasemodel struct {
	lbasemodel []ModelStructure
}
type ModelStructure struct {
	From string  	`json:"from"`
	Round uint64 	`json:"round"`
	B64model string `json:"b64model"`
}

type MulticastModelStructure struct {
	From string  	`json:"from"`
	Round uint64 	`json:"round"`
	PartB64model string `json:"partb64model"`
	Md5sum [16]byte `json:"md5sum"`
	Index uint32	`json:"length"`
	Total uint32	`json:"length"`
}

///////////////////////////////////////
type LIncomingModel struct {
	lincomingmodel []ModelStructure
}

type LBroadcastModel struct {
	lbroadcastmodel []ModelStructure
}
///////////////////////////////////////
//
//type queue struct {
//	q []interface{}
//}
//
//func Newqueue() *queue {
//	return &queue{}
//}
//
//func (q *queue) qlen()  int{
//	return int(len(q.q))
//}
//
//func (q *queue) aqueue(aq []interface{})  {
//
//	q.q = append(q.q , &queue{
//		aq
//	})
//	queue = queue[1:]   // Dequeue
//}