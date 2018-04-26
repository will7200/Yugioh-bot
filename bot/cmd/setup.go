package cmd

import (
	"github.com/spf13/cobra"
	"github.com/will7200/Yugioh-bot/bot/base"
)

// setupCmd represents the setup command
var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Get the bots up and running so that you can get going",
	Long:  `Setup will download tesseract if need be. Will Copy required files, hence forth.`,
	Run: func(cmd *cobra.Command, args []string) {
		base.Setup()
	},
}

func init() {
	rootCmd.AddCommand(setupCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// setupCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// setupCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
