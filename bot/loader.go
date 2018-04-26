package bot

import "github.com/yuin/gopher-lua"

func Loader(L *lua.LState) int {
	// register functions to the table
	mod := L.SetFuncs(L.NewTable(), exports)
	// register other stuff
	L.SetField(mod, "name", lua.LString("register"))

	// returns the module
	L.Push(mod)
	return 1
}

var exports = map[string]lua.LGFunction{
	"register_playmode": LRegisterPlayMode,
	"get_playmode":      LGetPlayMode,
}

func LRegisterPlayMode(L *lua.LState) int {
	RegisterPlayMode(L.CheckString(1), L.CheckFunction(2))
	return 0
}

func LGetPlayMode(L *lua.LState) int {
	playmode, err := GetPlayMode(L.CheckString(1))
	L.Push(lua.LString(playmode))
	L.Push(lua.LString(err.Error()))
	return 2
}
