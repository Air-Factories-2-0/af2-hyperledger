package main

import (
	"github.com/hyperledger/fabric-chaincode-go/shim"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"

	"encoding/json"
	"errors"
)

// Asset alternativo, il valore viene sovrascritto e la media calcolata usando la history dei valori
type AssetUsingHistory struct {
	Gcode    string `json:"gcode"`
	Id       string `json:"id"`
	Piece    int    `json:"piece"`
	Result   int    `json:"result"`
	Snapshot string `json:"snapshot"`
}

func (sc *SmartContract) SaveAssetUsingHistory(ctx contractapi.TransactionContextInterface, key string, gcode string, snapshot string, piece int) error {

	result, err := getResult(gcode, snapshot)

	if err != nil {
		return err
	}

	asset := AssetUsingHistory{
		Id:       key,
		Result:   int(result),
		Snapshot: snapshot,
		Gcode:    gcode,
		Piece:    piece,
	}

	a, _ := json.Marshal(asset)

	return ctx.GetStub().PutState(key, a)
}

func (sc *SmartContract) GetAverageUsingHistory(ctx contractapi.TransactionContextInterface, key string) (*AverageQueryResult, error) {
	existing, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, err
	}

	if existing == nil {
		return nil, errors.New("asset does not exist")
	}

	history, err := ctx.GetStub().GetHistoryForKey(key)

	if err != nil {
		return nil, err
	}

	average, err := getAverageFromHistory(history)

	if err != nil {
		return nil, err
	}

	return average, nil
}

func (sc *SmartContract) GetAssetUsingHistory(ctx contractapi.TransactionContextInterface, key string) (*AssetQueryResult, error) {
	existing, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, err
	}

	if existing == nil {
		return nil, errors.New("asset does not exist")
	}

	history, err := ctx.GetStub().GetHistoryForKey(key)

	if err != nil {
		return nil, err
	}

	result, err := getAssetFromHistory(history, key)
	if err != nil {
		return nil, err
	}
	return result, nil
}

func getAssetFromHistory(history shim.HistoryQueryIteratorInterface, key string) (*AssetQueryResult, error) {

	asset := new(AssetQueryResult)

	asset.Id = key

	counter := make(map[int]int)
	sums := make(map[int]int)
	results := make(map[int][]*Result)

	for history.HasNext() {
		x, err := history.Next()
		if err != nil {
			return nil, err
		}
		a := new(AssetUsingHistory)
		json.Unmarshal(x.Value, a)
		results[a.Piece] = append(results[a.Piece], &Result{
			Gcode:    a.Gcode,
			Result:   a.Result,
			Snapshot: a.Snapshot,
		})
		counter[a.Piece]++
		sums[a.Piece] += a.Result
	}

	for piece, sum := range sums {

		item := AssetQueryResultItem{
			Average: sum / counter[piece],
			Piece:   piece,
			Results: results[piece],
		}
		asset.Assets = append(asset.Assets, &item)
	}
	return asset, nil
}

func (sc *SmartContract) TestSave1(ctx contractapi.TransactionContextInterface, key string, gcode string, snapshot string, piece int, value int) {

	asset := AssetUsingHistory{
		Id:       key,
		Result:   value,
		Snapshot: snapshot,
		Gcode:    gcode,
		Piece:    piece,
	}

	a, _ := json.Marshal(asset)
	ctx.GetStub().PutState(key, a)
}

func getAverageFromHistory(history shim.HistoryQueryIteratorInterface) (*AverageQueryResult, error) {

	counter := make(map[int]int)
	averages := make(map[int]int)
	for history.HasNext() {
		x, err := history.Next()
		if err != nil {
			return nil, err
		}
		a := new(AssetUsingHistory)
		json.Unmarshal(x.Value, a)

		counter[a.Piece]++
		averages[a.Piece] += a.Result
	}

	aq := new(AverageQueryResult)
	for piece := range averages {
		aq.Results = append(aq.Results, &AverageQueryResultItem{
			Average: averages[piece] / counter[piece],
			Piece:   piece,
		})
	}
	return aq, nil
}
