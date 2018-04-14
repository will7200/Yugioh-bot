package cmd

import (
	"github.com/spf13/cobra"
	"runtime"
	"github.com/will7200/Yugioh-bot/bot/base"
	"fmt"
)

// versionCmd represents the version command
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Prints the version of the bot -- Yu-gi-oh Duel Links",
	Long: `Keep Track of that version bot.`,
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
		fmt.Printf("Yu-gi-oh Duel Links Bot v%s-%s %s/%s Build Date: %s\n", base.Version, base.GitSummary, runtime.GOOS, runtime.GOARCH, base.BuildDate)
	}
}
