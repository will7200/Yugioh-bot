package cmd

import (
	"fmt"
	"os"
	"path"

	"github.com/mitchellh/go-homedir"
	"github.com/pelletier/go-toml"
	"github.com/spf13/afero"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot"
)

// configGenerateCmd represents the configGenerate command
var configGenerateCmd = &cobra.Command{
	Use:   "generate",
	Short: "Generate Config files",
	Long:  `Generates the standard config file associated with the Developers standards`,
	Run:   genConfig,
}

func init() {
	configCmd.AddCommand(configGenerateCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// configGenerateCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// configGenerateCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func genConfig(_ *cobra.Command, _ []string) {
	home, err := homedir.Dir()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	configFile := viper.ConfigFileUsed()
	if configFile == "" {
		configFile = path.Join(home, homeDir, configFileName)
	}
	appfs := afero.NewOsFs()
	if fileExists, err := afero.Exists(appfs, configFile); err == nil && fileExists {
		fmt.Printf("Config file %s exists already\n", configFile)
		return
	} else if err != nil {
		fmt.Errorf("%s", err)
		os.Exit(1)
	}
	appfs.MkdirAll(path.Dir(configFile), 0755)
	fmt.Printf("Creating file: %s\n", configFile)
	file, err := appfs.Create(configFile)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	config := getDefaultConfig()
	config.Bot.PersistenceLocation = path.Join(home, homeDir, persistanceFileName)
	err = toml.NewEncoder(file).Encode(*config)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	file.Close()
}

func getDefaultConfig() *bot.BotConfig {
	config := &bot.BotConfig{
		Title: "Duel Links Bot Config",
		Bot: bot.BotOptions{
			RunOnStartUp:         false,
			PersistenceLocation:  "",
			SleepFactor:          1,
			KillProviderOnFinish: false,
			PersistenceType:      "file",
		},
	}
	return config
}
