package cmd

import (
	"fmt"
	"os"
	"path"
	"runtime"
	"strings"

	"github.com/mattn/go-colorable"
	"github.com/mitchellh/go-homedir"
	plog "github.com/prometheus/common/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const (
	homeDir             = "DLBot"
	configFileName      = "yugioh-bot.toml"
	persistanceFileName = "RunTimePersistence.toml"

	logLevelName = "log.level"
)

var (
	cfgFile            string
	logLevel           string
	defaultFilePath    = path.Join("$HOME", homeDir, configFileName)
	messageDefaultFile = fmt.Sprintf("config file (%s)", defaultFilePath)
	log                = plog.NewPassedLoggerUnsourced(logrus.StandardLogger())
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "dlbot",
	Short: "Yugioh Duel Links Bot",
	Long:  `Yugioh Duel Links Bot for those nasty NPC and reward collections`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	//	Run: func(cmd *cobra.Command, args []string) { },
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(rootInit)

	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", messageDefaultFile)
	rootCmd.PersistentFlags().StringVar(&logLevel, "log-level", "info", "Change log level for bot")

	viper.BindPFlag(logLevelName, rootCmd.Flag("log-level"))

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
	viper.SetEnvPrefix("DLBOT")
	logrus.SetFormatter(&logrus.TextFormatter{ForceColors: true, FullTimestamp: true})
	if runtime.GOOS == "windows" {
		logrus.SetOutput(colorable.NewColorableStdout())
	}
}

// rootInit reads in config file and ENV variables if set.
func rootInit() {
	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
	} else {
		// Find home directory.
		home, err := homedir.Dir()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		// Search config in DLBot directory with name "yugioh-bot" (without extension).
		viper.AddConfigPath(path.Join(home, homeDir))
		// Search for a override config in the current directory
		viper.AddConfigPath(".")
		viper.SetConfigName("yugioh-bot")
	}

	viper.AutomaticEnv() // read in environment variables that match

	// If a config file is found, read it in.
	if err := viper.ReadInConfig(); err == nil {
		if !strings.Contains(strings.Join(os.Args, " "), "completion") {
			fmt.Println("Using config file:", viper.ConfigFileUsed())
		}
	}
	if logLevel != "" {
		level, err := logrus.ParseLevel(logLevel)
		if err != nil {
			logrus.Panicf("Invalid level: %s\n", logLevel)
		}
		logrus.SetLevel(level)
		if level == logrus.DebugLevel {
			log = plog.NewPassedLogger(logrus.StandardLogger())
		}
	}
}
func getConfigFile() string {
	home, err := homedir.Dir()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	configFile := viper.ConfigFileUsed()
	if configFile == "" {
		configFile = path.Join(home, homeDir, configFileName)
	}
	return configFile
}
