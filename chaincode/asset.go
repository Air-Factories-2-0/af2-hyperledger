package main

import (
	"io"
	"os"
	"os/exec"

	shell "github.com/ipfs/go-ipfs-api"

	"strconv"
	"strings"
	"unicode"
)

type Asset struct {
	Id   string        `json:"id"`
	Data map[int]*Data `json:"data"`
}

type Data struct {
	Average int       `json:"average"`
	Results []*Result `json:"results"`
}

type Result struct {
	Gcode    string `json:"gcode"`
	Result   int    `json:"result"`
	Snapshot string `json:"snapshot"`
}

type AverageQueryResultItem struct {
	Average int `json:"average"`
	Piece   int `json:"piece"`
}

type AverageQueryResult struct {
	Results []*AverageQueryResultItem `json:"results"`
}

type AssetQueryResult struct {
	Id     string                  `json:"id"`
	Assets []*AssetQueryResultItem `json:"assets"`
}

type AssetQueryResultItem struct {
	Average int       `json:"average"`
	Piece   int       `json:"piece"`
	Results []*Result `json:"results"`
}

// legge i file da ipfs, scrive i contenuti su file temporanei, quindi li passa alla
// funzione per calcolare il risultato
func getResult(gcode string, snapshot string) (int, error) {
	sh := shell.NewShell("ipfs_host:5001")

	// lettura dei file di ipfs
	gcodeReader, err := sh.Cat(gcode)

	if err != nil {
		return -1, err
	}
	defer gcodeReader.Close()

	// scrittura su file temporaneo
	gcodeFile, err := os.CreateTemp(os.TempDir(), "GCODE_")

	if err != nil {
		return -1, err
	}
	_, err = io.Copy(gcodeFile, gcodeReader)
	if err != nil {
		return -1, err
	}

	snapshotReader, err := sh.Cat(snapshot)

	if err != nil {
		return -1, err
	}
	defer snapshotReader.Close()

	snapshotFile, err := os.CreateTemp(os.TempDir(), "SNAP_")

	if err != nil {
		return -1, err
	}

	_, err = io.Copy(snapshotFile, snapshotReader)

	if err != nil {
		return -1, err
	}

	result, err := calculateResult(gcodeFile.Name(), snapshotFile.Name())

	if err != nil {
		return -1, err
	}
	return int(result), nil
}

// funzione per rimuovere il whitespace dal risultato che lo script di python scrive sullo std output
func stripSpaces(str string) string {
	return strings.Map(func(r rune) rune {
		if unicode.IsSpace(r) {
			// if the character is a space, drop it
			return -1
		}
		// else keep it in the string
		return r
	}, str)
}

// calcola e restituisce il risultato eseguendo lo script di python
func calculateResult(a string, b string) (int, error) {
	cmd := exec.Command("python", "/go/script.py", a, b)

	out, err := cmd.Output()
	if err != nil {
		return -1, err
	}
	res := stripSpaces(string(out))

	result, err := strconv.ParseInt(res, 10, 0)
	if err != nil {
		return -1, err
	}
	return int(result), nil
}
