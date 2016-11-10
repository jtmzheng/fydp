package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
)

type RawMicData struct {
	NumSamples int    `json:"NumSamples"`
	Data       string `json:"Data"`
}

type MicData struct {
	Name string
	Data [3][]int
}

func UnInterleave(data *RawMicData) *MicData {
	str := data.Data[2:len(data.Data)]
	mic := MicData{Name: "temp"}
	for i := 0; i+2 < len(str); i += 2 {
		c, _ := strconv.ParseInt(str[i:i+2], 16, 0)
		mic.Data[(i/2)%3] = append(mic.Data[(i/2)%3], int(c))
	}

	return &mic
}

func (mic *MicData) WriteCsv(name string) error {
	file, err := os.Create(name)
	if err != nil {
		return err
	}

	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, arr := range mic.Data {
		starr := make([]string, len(arr), len(arr))
		for i, val := range arr {
			starr[i] = strconv.Itoa(val)
		}

		err := writer.Write(starr)
		if err != nil {
			return err
		}
	}
	return nil
}

func main() {
	path := flag.String("path", "./tmp.json", "Path to json file to parse")
	outPath := flag.String("out", "./tmp.csv", "Path to csv file to output")

	flag.Parse()

	file, err := ioutil.ReadFile(*path)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		os.Exit(1)
	}

	var data RawMicData
	json.Unmarshal(file, &data)
	fmt.Printf("NumSamples %v, len(data) %v\n", data.NumSamples, len(data.Data))
	test := UnInterleave(&data)
	test.WriteCsv(*outPath)
	fmt.Printf("Done writing csv to %v\n", *outPath)
}
