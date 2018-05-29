package dl

import (
	"gocv.io/x/gocv"
)

// DuelLinksInstanceInfo
type DuelLinksInstanceInfo struct {
	X, Y, Page int
	Status     string
	Name       string
}

type DuelLinks interface {
	GetCurrentPage(mat *gocv.Mat)
	InitialScreen(started bool) (bool, error)
	ScanFor()
	WaitFor()
}

type BaseDuelLinks struct {
	SleepFactor float64
	provider    Provider
}

func (*BaseDuelLinks) ScanFor() {
	panic("implement me")
}

func (*BaseDuelLinks) GetCurrentPage(mat *gocv.Mat) {
	log.Panic("implement me")
}

func (*BaseDuelLinks) InitialScreen(bool) (bool, error) {
	log.Panic("implement me")
	return false, nil
}

func (*BaseDuelLinks) WaitFor() {
	log.Panic("implement me")
}

func NewDuelLinks(no *Options) DuelLinks {
	return &BaseDuelLinks{
		no.SleepFactor,
		no.Provider,
	}
}
