package providers

import "gocv.io/x/gocv"

// Miscellaneous all functions that don't fall under actions or are bot specific
// fall under here
type Miscellaneous interface {
	IsProcessRunning() bool
	StartProcess()
	KillProcess()
	EnsureResolutionMatches(mat *gocv.Mat)
	// Ensures that every is ok
	PreCheck() error
}

type BaseMiscellaneous struct {
	provider Provider
}

func (*BaseMiscellaneous) PreCheck() error {
	panic("implement me")
}

func (*BaseMiscellaneous) IsProcessRunning() bool {
	//log.Panic("implement me")
	return true
}

func (*BaseMiscellaneous) StartProcess() {
	log.Panic("implement me")
}

func (*BaseMiscellaneous) KillProcess() {
	log.Panic("implement me")
}

func (*BaseMiscellaneous) EnsureResolutionMatches(mat *gocv.Mat) {
	log.Panic("implement me")
}

func NewMisc(o *Options) Miscellaneous {
	misc := new(DuelLinksMisc)
	misc.provider = o.Provider
	return misc
}
