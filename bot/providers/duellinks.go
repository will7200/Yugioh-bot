package providers

import (
	"gocv.io/x/gocv"
	"github.com/spf13/afero"
	rbt "github.com/emirpasic/gods/trees/redblacktree"
)

type DuelLinksInstanceInfo struct {
	X, Y, Page int
	Status     string
	Name       string
}
type Correlation int
type ComparatorInfo struct {
	registered *rbt.Tree
}
type ComparatorData struct {
	Asset string // compare image against
	Thresholds struct {
		XThreshold, YThreshold int
	}
}

func (c *ComparatorInfo) Prepare(key string) error {
	panic("implement me")
}

func (c *ComparatorInfo) Register(key string, asset afero.Fs, data afero.Fs) {

	c.registered.Put(key, data)
}

func (c *ComparatorInfo) Compare(img *gocv.Mat, info *DuelLinksInstanceInfo, correlation Correlation) {
	//c.registered.Get()
}

type Comparator interface {
	Register(key string, asset afero.Fs, data afero.Fs)
	Prepare(key string) error
	Compare(img *gocv.Mat, info *DuelLinksInstanceInfo, correlation Correlation)
}

func NewComparator() Comparator {
	tree := rbt.NewWithStringComparator()
	return &ComparatorInfo{
		tree,
	}
}

type DuelLinks interface {
	Auto()
	MethodName()
	CompareWithCancelButton()
	CompareWithBackButton()
	Scan()
	ScanForOk()
	ScanForClose()
	ClickAutoDuel()
	DetermineAutoDuelStatus()
	Battle()
	CheckBattle()
	CheckIfBattleIsRunning()
	CheckIfBattle()
	VerifyBattle()
	PassThroughInitialScreen()
	WaitFor()
	WaitForAutoDuel()
	WaitForWhiteBottom()
	GetCurrentPage(mat *gocv.Mat)
}

type BaseDuelLinks struct {
	CurrentRun  int
	SleepFactor int
	provider    Provider
}

func (*BaseDuelLinks) GetCurrentPage(mat *gocv.Mat) {
	panic("implement me")
}

func (*BaseDuelLinks) Auto() {
	panic("implement me")
}

func (*BaseDuelLinks) CheckIfBattleIsRunning() {
	panic("implement me")
}

func (*BaseDuelLinks) CheckBattle() {
	panic("implement me")
}

func (*BaseDuelLinks) Scan() {
	panic("implement me")
}

func (*BaseDuelLinks) MethodName() {
	panic("implement me")
}

func (*BaseDuelLinks) CompareWithCancelButton() {
	panic("implement me")
}

func (*BaseDuelLinks) CompareWithBackButton() {
	panic("implement me")
}

func (*BaseDuelLinks) ScanForOk() {
	panic("implement me")
}

func (*BaseDuelLinks) ScanForClose() {
	panic("implement me")
}

func (*BaseDuelLinks) ClickAutoDuel() {
	panic("implement me")
}

func (*BaseDuelLinks) DetermineAutoDuelStatus() {
	panic("implement me")
}

func (*BaseDuelLinks) Battle() {
	panic("implement me")
}

func (*BaseDuelLinks) CheckIfBattle() {
	panic("implement me")
}

func (*BaseDuelLinks) VerifyBattle() {
	panic("implement me")
}

func (*BaseDuelLinks) PassThroughInitialScreen() {
	panic("implement me")
}

func (*BaseDuelLinks) WaitFor() {
	panic("implement me")
}

func (*BaseDuelLinks) WaitForAutoDuel() {
	panic("implement me")
}

func (*BaseDuelLinks) WaitForWhiteBottom() {
	panic("implement me")
}

func NewDuelLinks(no *Options) DuelLinks {
	return &BaseDuelLinks{
		0,
		no.SleepFactor,
		no.Provider,
	}
}
