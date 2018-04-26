package cmd

import (
	"github.com/spf13/cobra"
)

// guiCmd represents the gui command
var guiCmd = &cobra.Command{
	Use:   "steam",
	Short: "Starts a bot instance using the steam app",
	Long:  `Starts a bot using the Yu-gi-oh App from steam. This is limited to max one instance per machine.`,
	Run: func(cmd *cobra.Command, args []string) {
		log.Panic("steam not implemented yet")
	},
}

func init() {
	runCmd.AddCommand(guiCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// guiCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// guiCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
