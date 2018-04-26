package cmd

import (
	"fmt"
	"os"

	"github.com/pelletier/go-toml"
	"github.com/spf13/afero"
	"github.com/spf13/cobra"
)

// configChangeCmd represents the configChange command
var configChangeCmd = &cobra.Command{
	Use:   "change [parameter] [value]",
	Short: "Change config values",
	Long: `This command will allow you to change config values without having to 
open a file`,
	Run: func(cmd *cobra.Command, args []string) {
		appfs := afero.NewOsFs()
		file, err := appfs.Open(getConfigFile())
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		tree, err := toml.LoadReader(file)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		tree.Set(args[0], args[1])
		tmpfile, err := afero.TempFile(appfs, "", "temp-dlbot.toml")
		_, err = tree.WriteTo(tmpfile)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		file.Close()
		tmpfile.Close()
		appfs.Rename(tmpfile.Name(), file.Name())
	},
}

func init() {
	configCmd.AddCommand(configChangeCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// configChangeCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// configChangeCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
