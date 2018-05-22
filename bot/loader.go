package bot

import "github.com/yuin/gopher-lua"

func RunTimeLoader(rt *runTime) func(*lua.LState) int {
	return func(L *lua.LState) int {

		rtLua := NewRunTimeLua(rt)
		// register functions to the table
		var exports = map[string]lua.LGFunction{
			"register_playmode": LRegisterPlayMode,
			"get_playmode":      LGetPlayMode,
			"current_playmode":  rtLua.LCurrentPlayMode,
		}
		mod := L.SetFuncs(L.NewTable(), exports)
		// register other stuff
		L.SetField(mod, "name", lua.LString("rt"))

		// returns the module
		L.Push(mod)
		return 1
	}
}

// LuaProvider methods exposed in lua engine
type RunTimeLua struct {
	rt *runTime
}

// NewLuaProvider returns a lua provider instance
func NewRunTimeLua(rt *runTime) *RunTimeLua {
	return &RunTimeLua{rt: rt}
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

func (Rt *RunTimeLua) LCurrentPlayMode(L *lua.LState) int {
	playmode := Rt.rt.options.PlayMode
	if playmode == "" {
		playmode = "auto"
	}
	L.Push(lua.LString(string(playmode)))
	return 1
}
