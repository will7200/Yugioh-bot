package cmd

import (
	"strings"

	"github.com/fsnotify/fsnotify"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot/base"
)

const (
	botWorkers     = "bot.workers"
	botSleepFactor = "bot.SleepFactor"
)

var (
	watchConfig bool
	runAsGui    bool
)

// runCmd represents the run command
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Starts the bot",
	Long:  ``,
}

func init() {
	cobra.OnInitialize(cobraRunInit)
	rootCmd.AddCommand(runCmd)
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	runCmd.PersistentFlags().BoolVar(&watchConfig, "watch-config", false, "Reload Bot on config change")
	runCmd.PersistentFlags().BoolVar(&runAsGui, "gui-interface", false, "Run the bot as a gui interface")
	runCmd.PersistentFlags().Int("workers", 4, "Amount of concurrency workers for jobs to use")
	viper.BindPFlag(botWorkers, runCmd.Flag("workers"))
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// runCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// runCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func cobraRunInit() {
	if watchConfig {
		logrus.Infof("Watching config file(%s) for changes", viper.ConfigFileUsed())
		viper.WatchConfig()
		viper.OnConfigChange(func(e fsnotify.Event) {
			base.ConfigChanged(e)
		})
	}
}
