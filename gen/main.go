package main

import (
	"fmt"

	"os"
	"github.com/dave/jennifer/jen"
	"log"
)

var registerGenerators map[string]func()*jen.File

const (
	provider    = "LuaProvider"
	loader      = "ProviderLoader"
	impersonate = "providers"
	gopherLua   = "github.com/yuin/gopher-lua"
)

func init() {
	registerGenerators = make(map[string]func()*jen.File)
	registerGenerators["luaprovider"] = luaprovider
}
func main() {
	if len(os.Args) < 2 {
		log.Panic("Not Going to work")
	}
	fmt.Println(os.Args)
	f := registerGenerators[os.Args[1]]()
	if len(os.Args) == 3 {
		err := f.Save(os.Args[1])
		if err != nil {
			fmt.Println(err)
			panic(err)
		}
	} else {
		//fmt.Printf("%#v", f)
	}
}
