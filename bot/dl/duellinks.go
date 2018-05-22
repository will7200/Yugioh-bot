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
	Battle()
	CheckBattle()
	CheckIfBattle()
	DetermineAutoDuelStatus()
	GetCurrentPage(mat *gocv.Mat)
	PassThroughInitialScreen(started bool) error
	ScanFor()
	Scan()
	VerifyBattle()
	WaitFor()
}

type BaseDuelLinks struct {
	CurrentRun  int
	SleepFactor float64
	provider    Provider
}

func (*BaseDuelLinks) ScanFor() {
	panic("implement me")
}

func (*BaseDuelLinks) GetCurrentPage(mat *gocv.Mat) {
	log.Panic("implement me")
}

func (*BaseDuelLinks) CheckIfBattleIsRunning() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) CheckBattle() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) Scan() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) MethodName() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) DetermineAutoDuelStatus() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) Battle() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) CheckIfBattle() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) VerifyBattle() {
	log.Panic("implement me")
}

func (*BaseDuelLinks) PassThroughInitialScreen(bool) error {
	log.Panic("implement me")
	return nil
}

func (*BaseDuelLinks) WaitFor() {
	log.Panic("implement me")
}

func NewDuelLinks(no *Options) DuelLinks {
	return &BaseDuelLinks{
		0,
		no.SleepFactor,
		no.Provider,
	}
}
