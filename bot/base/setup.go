package base

import (
	"github.com/fatih/color"
)

func Setup() {
	color.New(color.FgCyan).Add(color.Underline).Println("Running Setup Command")
	color.New(color.BgCyan).Printf("" +
		"Installing required files and components to get this bot up and running")
	color.New().Println("")
}
