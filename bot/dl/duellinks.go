package dl

// DuelLinksInstanceInfo
type DuelLinksInstanceInfo struct {
	X, Y, Page int
	Status     string
	Name       string
}

type DuelLinks interface {
	InitialScreen(started bool) (bool, error)
	ScanFor()
	SpecialEvents(info DuelLinksInstanceInfo)
	WaitFor()
}

type BaseDuelLinks struct {
	provider Provider
}

func (*BaseDuelLinks) SpecialEvents(info DuelLinksInstanceInfo) {
	panic("implement me")
}

func (*BaseDuelLinks) ScanFor() {
	panic("implement me")
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
		no.Provider,
	}
}
