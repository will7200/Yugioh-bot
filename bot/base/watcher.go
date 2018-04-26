package base

import (
	"github.com/fsnotify/fsnotify"
	"github.com/spf13/viper"
)

func ConfigChanged(e fsnotify.Event) {
	log.Warn("Config Change was detected reloading application as soon as possible")
	if err := viper.ReadInConfig(); err == nil {
		log.Warn("Reread config file: ", viper.ConfigFileUsed())
	} else {
		log.Error("Error rereading config file: ", err)
	}
}
