package cmd

import (
	"fmt"
	"runtime"

	"github.com/spf13/cobra"
	"github.com/will7200/Yugioh-bot/bot/base"
)

// versionCmd represents the version command
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Displays the version of the bot",
	Long:  `Keep Track of that version bot.`,
	Run: func(cmd *cobra.Command, args []string) {
		printVersion()
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)
}

func printVersion() {
	if base.GitCommit == "" {
		fmt.Printf("Yu-gi-oh Duel Links Bot v%s %s/%s Build Date: %s\n", base.Version, runtime.GOOS, runtime.GOARCH, base.BuildDate)
	} else {
		fmt.Printf("Yu-gi-oh Duel Links Bot %s %s/%s Build Date: %s\n", base.GitSummary, runtime.GOOS, runtime.GOARCH, base.BuildDate)
	}
}
