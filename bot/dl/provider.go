package dl

// Provider abstracts away different providers to have a uniform api
type Provider interface {
	Actions
	DuelLinks
	Miscellaneous
}

// BaseProvider unifies all interfaces that the bot needs
// Each provider should inherit this or like this (composition really)
type BaseProvider struct {
	Actions
	DuelLinks
	Miscellaneous
}

// NewBaseProvider return a new Provider with all sub-components actualized
func NewBaseProvider(no *Options) Provider {
	return &BaseProvider{
		NewActions(no),
		NewDuelLinks(no),
		NewMisc(no),
	}
}
