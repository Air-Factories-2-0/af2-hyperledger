package main

import (
	"encoding/json"
	"errors"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

func (sc *SmartContract) SaveAsset(ctx contractapi.TransactionContextInterface, key string, gcode string, snapshot string, piece int) error {
	r, err := getResult(gcode, snapshot)
	if err != nil {
		return err
	}

	result := Result{
		Gcode:    gcode,
		Result:   r,
		Snapshot: snapshot,
	}

	existing, err := ctx.GetStub().GetState(key)

	if err != nil {
		return err
	}

	if existing == nil {
		asset := Asset{
			Id: key,
			Data: map[int]*Data{
				piece: {
					Average: r,
					Results: []*Result{&result},
				},
			},
		}

		assetBytes, err := json.Marshal(asset)

		if err != nil {
			return err
		}
		return ctx.GetStub().PutState(key, assetBytes)
	}
	asset := new(Asset)
	err = json.Unmarshal(existing, asset)

	if err != nil {
		return err
	}

	_, exists := asset.Data[piece]

	if exists {
		size := len(asset.Data[piece].Results)
		asset.Data[piece].Average = (asset.Data[piece].Average*size + r) / (size + 1)
		asset.Data[piece].Results = append(asset.Data[piece].Results, &result)
	} else {
		asset.Data[piece] = &Data{
			Average: r,
			Results: []*Result{&result},
		}
	}

	assetBytes, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(key, assetBytes)
}

// func (sc *SmartContract) GetAsset(ctx contractapi.TransactionContextInterface, key string) (string, error) {
// 	a, err := ctx.GetStub().GetState(key)
// 	if err != nil {
// 		return "", err
// 	}
// 	return string(a), nil
// }

func (sc *SmartContract) GetAsset(ctx contractapi.TransactionContextInterface, key string) (*AssetQueryResult, error) {
	existing, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, err
	}

	if existing == nil {
		return nil, errors.New("asset not found")
	}

	asset := new(Asset)
	err = json.Unmarshal(existing, asset)
	if err != nil {
		return nil, err
	}

	result := new(AssetQueryResult)
	result.Id = key

	for key, data := range asset.Data {
		item := AssetQueryResultItem{
			Average: data.Average,
			Piece:   key,
			Results: data.Results,
		}
		result.Assets = append(result.Assets, &item)
	}
	return result, nil
}

// usata per testing decidendo arbitrariamente il valore del risultato
func (sc *SmartContract) TestSave(ctx contractapi.TransactionContextInterface, key string, gcode string, snapshot string, piece int, result int) error {
	existing, err := ctx.GetStub().GetState(key)
	if err != nil {
		return err
	}

	res := Result{
		Gcode:    gcode,
		Result:   result,
		Snapshot: snapshot,
	}
	if existing == nil {
		asset := Asset{
			Id: key,
			Data: map[int]*Data{
				piece: {
					Average: result,
					Results: []*Result{&res},
				},
			},
		}
		bytes, err := json.Marshal(asset)
		if err != nil {
			return err
		}
		return ctx.GetStub().PutState(key, bytes)
	}
	asset := new(Asset)
	err = json.Unmarshal(existing, asset)
	if err != nil {
		return err
	}

	_, exists := asset.Data[piece]

	if exists {
		size := len(asset.Data[piece].Results)
		asset.Data[piece].Average = (asset.Data[piece].Average*size + result) / (size + 1)
		asset.Data[piece].Results = append(asset.Data[piece].Results, &res)
	} else {
		asset.Data[piece] = &Data{
			Average: result,
			Results: []*Result{&res},
		}
	}

	bytes, err := json.Marshal(asset)
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(key, bytes)
}

func (sc *SmartContract) GetAverage(ctx contractapi.TransactionContextInterface, key string) (*AverageQueryResult, error) {
	existing, err := ctx.GetStub().GetState(key)

	if err != nil {
		return nil, err
	}

	if existing == nil {
		return nil, errors.New("asset does not exist")
	}

	asset := new(Asset)
	err = json.Unmarshal(existing, asset)
	if err != nil {
		return nil, err
	}

	r := []*AverageQueryResultItem{}

	for piece, data := range asset.Data {
		r = append(r, &AverageQueryResultItem{
			Average: data.Average,
			Piece:   piece,
		})
	}

	result := AverageQueryResult{Results: r}
	return &result, nil
}
