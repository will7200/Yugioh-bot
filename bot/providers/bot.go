package providers

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
	panic("implement me")
}

func (*BaseBot) GuidedMode() {
	panic("implement me")
}

func (*BaseBot) PossibleBattlePoints() {
	panic("implement me")
}

func (*BaseBot) SpecialEvents(info DuelLinksInstanceInfo) {
	panic("implement me")
}

func (*BaseBot) SystemCall() {
	panic("implement me")
}

func (*BaseBot) ImgToString() {
	panic("implement me")
}

func NewBaseBot(o *Options) Bot {
	bot := &BaseBot{}
	bot.provider = o.Provider
	return bot
}
