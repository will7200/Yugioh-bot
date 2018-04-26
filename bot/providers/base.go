package providers

import (
	"fmt"

	"github.com/will7200/Yugioh-bot/bot/base"
)

var (
	log       = base.CheckWithSourcedLog()
	providers = map[string]NewProvider{}
)

type Options struct {
	Path        string
	SleepFactor int
	Dispatcher  *base.Dispatcher
	Provider    Provider
	IsRemote    bool
}

type NewProvider func(options *Options) Provider

func RegisterProvider(name string, value NewProvider) {
	providers[name] = value
}

func GetProvider(name string, options *Options) Provider {
	if val, ok := providers[name]; ok {
		return val(options)
	}
	fmt.Println(providers)
	panic(fmt.Sprintf("Could not Get Provider %s", name))
	return nil
}
