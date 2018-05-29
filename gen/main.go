package main

import (
	"fmt"
	"log"
	"os"

	"github.com/dave/jennifer/jen"
)

var registerGenerators map[string]func() *jen.File

const (
	provider    = "LuaProvider"
	loader      = "ProviderLoader"
	impersonate = "dl"
	gopherLua   = "github.com/yuin/gopher-lua"
)

func init() {
	registerGenerators = make(map[string]func() *jen.File)
	registerGenerators["luaprovider"] = luaprovider
	registerGenerators["luadetector"] = luadetector
}
func main() {
	if len(os.Args) < 2 {
		log.Panic("Not Going to work")
	}
	fmt.Println(os.Args)
	f := registerGenerators[os.Args[1]]()
	if len(os.Args) == 3 {
		err := f.Save(os.Args[2])
		if err != nil {
			fmt.Println(err)
			panic(err)
		}
	} else {
		//fmt.Printf("%#v", f)
	}
}
