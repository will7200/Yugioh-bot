package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

// completionCmd represents the completion command
var completionCmd = &cobra.Command{
	Use:   "completion",
	Short: "Generates bash completion scripts",
	Long: `
To configure your bash shell to load completions for each session add to your bashrc
By default completion code is written to stdout, e.g.:

MacOS
$ dlbot completion >> ~/.bash_profile

*nix
$ sudo dlbot completion >> /etc/bash_completion.d

Alternatives ~/.bashrc or ~/.profile or ~/.bash_profile 
`,
	Run: func(cmd *cobra.Command, args []string) {
		rootCmd.GenBashCompletion(os.Stdout)
	},
}

func init() {
	rootCmd.AddCommand(completionCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// completetionCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// completetionCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
