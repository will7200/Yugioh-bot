package cmd

import (
	"path"
	"strings"

	"github.com/fsnotify/fsnotify"
	"github.com/mitchellh/go-homedir"
	"github.com/sirupsen/logrus"
	"github.com/spf13/afero"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/will7200/Yugioh-bot/bot/dl"
)

const (
	botWorkers     = "bot.workers"
	botSleepFactor = "bot.SleepFactor"

	defaultDataFileName = "data.xml"
	dataMalformedKey    = "data.malformed"
	dataFileKey         = "data.file"
)

var (
	watchConfig         bool
	runAsGui            bool
	dataFile            string
	dataMalformed       bool
	home, _             = homedir.Dir()
	defaultDataFilePath = path.Join(home, homeDir, defaultDataFileName)
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
	runCmd.PersistentFlags().StringVar(&dataFile, "data-file", defaultDataFilePath, "read in data file")
	runCmd.PersistentFlags().BoolVar(&dataMalformed, "data-malformed", true, "fails when data file is malformed, otherwise read what was packaged with binary")

	viper.BindPFlag(botWorkers, runCmd.Flag("workers"))
	viper.BindPFlag(dataMalformedKey, rootCmd.Flag("data-malformed"))
	viper.BindPFlag(dataFileKey, rootCmd.Flag("data-file"))
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

func readDataFile(app afero.Fs) *dl.Predefined {
	exists, err := afero.Exists(app, dataFile)
	if err != nil {
		log.Fatal(err)
	}
	if exists {
		file, err := app.Open(dataFile)
		if err != nil {
			log.Fatal(err)
		}
		predefined, err := dl.ReadPredefined(file)
		if err != nil && !dataMalformed {
			log.Fatal(err)
		} else if err == nil {
			return predefined
		}
	} else {
		log.Warn("File dne")
		log.Warn(defaultDataFilePath)
	}
	log.Warn("Reading data bundled with binary, might be out dated")
	return dl.GetDefaultsPredefined()
}
