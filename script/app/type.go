package main

//import (
//	_ "fmt"
//	//"github.com/TomorrowWu/golang-algorithms/data-structures/queue"
//)

type LBasemodel struct {
	lbasemodel []ModelStructure
}
type ModelStructure struct {
	from string
	round uint64
	b64model string
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