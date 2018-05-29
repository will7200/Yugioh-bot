package dl

type Bot interface {
	SpecialEvents(info DuelLinksInstanceInfo)
	ImgToString()
}

type BaseBot struct {
	provider Provider
}

func (*BaseBot) SpecialEvents(info DuelLinksInstanceInfo) {
	log.Panic("implement me")
}

func (*BaseBot) ImgToString() {
	log.Panic("implement me")
}

func NewBaseBot(o *Options) Bot {
	bot := &BaseBot{}
	bot.provider = o.Provider
	return bot
}
