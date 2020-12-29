package main

import (
	//"github.com/orktes/go-torch"
	//"io"
	//b64 "encoding/base64"
	//"github.com/vmihailenco/msgpack"
	//"io/ioutil"
	"os"
	"os/exec"
	"fmt"
)

type AggregatorApplication struct {
	grpcip string
	tmppath string
}

func NewAggregator(Grpcip string) *AggregatorApplication {
	return &AggregatorApplication{
		grpcip: Grpcip,
	}
}

func (app *AggregatorApplication) SetTmpPath(path string){
	app.tmppath = path
}

func (app *AggregatorApplication) Aggregate(models []string) string{
	blankWriter := ""

	for i, s := range models{
		if i!=len(models){
			blankWriter = blankWriter + s + ","
		}
		blankWriter = blankWriter+s
	}

	writetxt(blankWriter, app.tmppath)

	out, err := exec.Command("python", "agg.py",app.tmppath).Output()

	if err != nil {
		panic(err)
	}
	//fmt.Printf("%s", out)
	fmt.Println("Aggregate done.")
	return  string(out)
}

func (app *AggregatorApplication)MulticastListening(address string){

}

func writetxt(s string, path string)  {
	file, err := os.Create(path)
	if err != nil {
		panic(err)
	}

	_, err = file.WriteString(s)
	if err != nil {
		panic(err)
	}
	defer file.Close()
}