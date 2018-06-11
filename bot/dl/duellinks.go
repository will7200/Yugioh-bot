package dl

// DuelLinksInstanceInfo
type DuelLinksInstanceInfo struct {
	X, Y, Page int
	Status     string
	Name       string
}

type DuelLinks interface {
	InitialScreen(started bool) (bool, error)
}

type BaseDuelLinks struct {
	provider Provider
}

func (*BaseDuelLinks) InitialScreen(bool) (bool, error) {
	log.Panic("implement me")
	return false, nil
}

func NewDuelLinks(no *Options) DuelLinks {
	return &BaseDuelLinks{
		no.Provider,
	}
}
