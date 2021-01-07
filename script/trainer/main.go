package main

import (
	"flag"
	trainer "github.com/BCFL/trainer"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"io/ioutil"
	"log"
)


var flagAddress string

func init() {
	flag.StringVar(&flagAddress, "grpcip", "140.113.164.150:63387", "address of grpc endpoint")
}

func main()  {
	flag.Parse()


	conn, err := grpc.Dial(flagAddress, grpc.WithInsecure())
	log.Printf("check")
	if err != nil {
		log.Fatalf("連線失敗：%v", err)
		return
	}
	defer conn.Close()

	// 建立新的 Calculator 客戶端，所以等一下就能夠使用 Calculator 的所有方法。
	c := trainer.NewTrainerClient(conn)

	log.Printf(flagAddress)

	// 傳送新請求到遠端 gRPC 伺服器 Calculator 中，並呼叫 Plus 函式，讓兩個數字相加。
	content, err := ioutil.ReadFile("/Users/tonyguo/Downloads/modelf.txt")

     if err != nil {
          log.Fatal(err)
     }
	mm:=string(content)

	//log.Printf(mm)

	//gotrain := &trainer.TrainInfo{
	//	Round:     1,
	//	BaseModel: mm,
	//}
	//
	//r, err2 := c.Train(context.Background(), gotrain)
	//if err2 != nil {
	//	log.Fatalf("無法執行 函式：%v", err2)
	//}


	for i:=0; i < 5; i++ {
		r, err2 := c.Train(context.Background(), &trainer.TrainInfo{
			Round:     1,
			BaseModel: mm,
		})
		if err2 != nil {
			log.Fatalf("無法執行 函式：%v", err2)
		}

		mm=r.GetResult()
	}

	log.Printf(mm)
}