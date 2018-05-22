package dl

// Provider abstracts away different providers to have a uniform api
type Provider interface {
	Bot
	Actions
	DuelLinks
	Miscellaneous
}

// BaseProvider unifies all interfaces that the bot needs
// Each provider should inherit this or like this (composition really)
type BaseProvider struct {
	Actions
	Bot
	DuelLinks
	Miscellaneous
}

// NewBaseProvider return a new Provider with all sub-components actualized
func NewBaseProvider(no *Options) Provider {
	return &BaseProvider{
		NewActions(no),
		NewBaseBot(no),
		NewDuelLinks(no),
		NewMisc(no),
	}
}
