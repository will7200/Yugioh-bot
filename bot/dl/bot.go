package dl

type Bot interface {
	BattleMode(battle, version, info string)
	GuidedMode()
	PossibleBattlePoints()
	SpecialEvents(info DuelLinksInstanceInfo)
	SystemCall()
	ImgToString()
}

type BaseBot struct {
	provider Provider
}

func (*BaseBot) BattleMode(battle, version, info string) {
	log.Panic("implement me")
}

func (*BaseBot) GuidedMode() {
	log.Panic("implement me")
}

func (*BaseBot) PossibleBattlePoints() {
	log.Panic("implement me")
}

func (*BaseBot) SpecialEvents(info DuelLinksInstanceInfo) {
	log.Panic("implement me")
}

func (*BaseBot) SystemCall() {
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
