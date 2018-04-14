package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// botCmd represents the bot command
var botCmd = &cobra.Command{
	Use:   "bot",
	Short: "Starts the bot -- for gui haters basically",
	Long: `Starts the bot with no ui controls`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("bot called")
	},
}

func init() {
	rootCmd.AddCommand(botCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// botCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// botCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
