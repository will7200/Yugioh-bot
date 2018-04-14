// Copyright © 2018 NAME HERE <EMAIL ADDRESS>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"github.com/spf13/cobra"
	"runtime"
	"strings"
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
	if base.CommitHash == "" {
		fmt.Printf("Yu-gi-oh Duel Links Bot v%s %s/%s Build Date: %s\n", base.Version, runtime.GOOS, runtime.GOARCH, base.BuildDate)
	} else {
		fmt.Printf("Yu-gi-oh Duel Links Bot v%s-%s %s/%s Build Date: %s\n", base.Version, strings.ToUpper(base.CommitHash), runtime.GOOS, runtime.GOARCH, base.BuildDate)
	}
}
