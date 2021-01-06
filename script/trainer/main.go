package main

import (
	"flag"
	"github.com/BCFL/trainer"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"log"
)


var flagAddress string

func init() {
	flag.StringVar(&flagAddress, "grpcip", "localhost:62287", "address of grpc endpoint")
}

func main()  {
	flag.Parse()


	conn, err := grpc.Dial(flagAddress, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("連線失敗：%v", err)
	}
	defer conn.Close()

	// 建立新的 Calculator 客戶端，所以等一下就能夠使用 Calculator 的所有方法。
	c := trainer.NewTrainerClient(conn)

	// 傳送新請求到遠端 gRPC 伺服器 Calculator 中，並呼叫 Plus 函式，讓兩個數字相加。
	gotrain := &trainer.TrainInfo{
		Round:     0,
		BaseModel: "1323",
	}

	r, err := c.Train(context.Background(), gotrain)
	if err != nil {
		log.Fatalf("無法執行 Plus 函式：%v", err)
	}
	log.Printf("回傳結果：%d", r.Result)
}