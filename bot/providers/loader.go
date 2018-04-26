package providers

import (
	"github.com/yuin/gopher-lua"
	"gocv.io/x/gocv"
)

// ProviderLoader loads all exposed provider methods
func ProviderLoader(provider Provider) func(*lua.LState) int {
	return func(L *lua.LState) int {
		luaProvider := NewLuaProvider(provider)
		exports := map[string]lua.LGFunction{
			"auto":                        luaProvider.Auto,
			"battle":                      luaProvider.Battle,
			"battle_mode":                 luaProvider.BattleMode,
			"check_battle":                luaProvider.CheckBattle,
			"check_if_battle":             luaProvider.CheckIfBattle,
			"check_if_battle_is_running":  luaProvider.CheckIfBattleIsRunning,
			"click_auto_duel":             luaProvider.ClickAutoDuel,
			"compare_with_back_button":    luaProvider.CompareWithBackButton,
			"compare_with_cancel_button":  luaProvider.CompareWithCancelButton,
			"determine_auto_duel_status":  luaProvider.DetermineAutoDuelStatus,
			"ensure_resolution_matches":   luaProvider.EnsureResolutionMatches,
			"get_current_page":            luaProvider.GetCurrentPage,
			"guided_mode":                 luaProvider.GuidedMode,
			"img_to_string":               luaProvider.ImgToString,
			"is_process_running":          luaProvider.IsProcessRunning,
			"kill_process":                luaProvider.KillProcess,
			"method_name":                 luaProvider.MethodName,
			"pass_through_initial_screen": luaProvider.PassThroughInitialScreen,
			"possible_battle_points":      luaProvider.PossibleBattlePoints,
			"scan":                        luaProvider.Scan,
			"scan_for_close":              luaProvider.ScanForClose,
			"scan_for_ok":                 luaProvider.ScanForOk,
			"special_events":              luaProvider.SpecialEvents,
			"start_process":               luaProvider.StartProcess,
			"swipe":                       luaProvider.Swipe,
			"swipe_right":                 luaProvider.SwipeRight,
			"swipe_time":                  luaProvider.SwipeTime,
			"system_call":                 luaProvider.SystemCall,
			"take_png_screen_shot":        luaProvider.TakePNGScreenShot,
			"tap":                         luaProvider.Tap,
			"verify_battle":               luaProvider.VerifyBattle,
			"wait_for":                    luaProvider.WaitFor,
			"wait_for_auto_duel":          luaProvider.WaitForAutoDuel,
			"wait_for_ui":                 luaProvider.WaitForUi,
			"wait_for_white_bottom":       luaProvider.WaitForWhiteBottom,
		}
		mod := L.SetFuncs(L.NewTable(), exports)
		L.SetField(mod, "name", lua.LString("provider"))
		L.Push(mod)
		return 1
	}
}

// LuaProvider methods exposed in lua engine
type LuaProvider struct {
	provider Provider
}

// NewLuaProvider returns a lua provider instance
func NewLuaProvider(provider Provider) *LuaProvider {
	return &LuaProvider{provider: provider}
}

// Auto wrapper for lua engine
func (lua *LuaProvider) Auto(L *lua.LState) int {
	lua.provider.Auto()
	return 0
}

// Battle wrapper for lua engine
func (lua *LuaProvider) Battle(L *lua.LState) int {
	lua.provider.Battle()
	return 0
}

// BattleMode wrapper for lua engine
func (lua *LuaProvider) BattleMode(L *lua.LState) int {
	lua.provider.BattleMode(L.CheckString(1), L.CheckString(2), L.CheckString(3))
	return 0
}

// CheckBattle wrapper for lua engine
func (lua *LuaProvider) CheckBattle(L *lua.LState) int {
	lua.provider.CheckBattle()
	return 0
}

// CheckIfBattle wrapper for lua engine
func (lua *LuaProvider) CheckIfBattle(L *lua.LState) int {
	lua.provider.CheckIfBattle()
	return 0
}

// CheckIfBattleIsRunning wrapper for lua engine
func (lua *LuaProvider) CheckIfBattleIsRunning(L *lua.LState) int {
	lua.provider.CheckIfBattleIsRunning()
	return 0
}

// ClickAutoDuel wrapper for lua engine
func (lua *LuaProvider) ClickAutoDuel(L *lua.LState) int {
	lua.provider.ClickAutoDuel()
	return 0
}

// CompareWithBackButton wrapper for lua engine
func (lua *LuaProvider) CompareWithBackButton(L *lua.LState) int {
	lua.provider.CompareWithBackButton()
	return 0
}

// CompareWithCancelButton wrapper for lua engine
func (lua *LuaProvider) CompareWithCancelButton(L *lua.LState) int {
	lua.provider.CompareWithCancelButton()
	return 0
}

// DetermineAutoDuelStatus wrapper for lua engine
func (lua *LuaProvider) DetermineAutoDuelStatus(L *lua.LState) int {
	lua.provider.DetermineAutoDuelStatus()
	return 0
}

// EnsureResolutionMatches wrapper for lua engine
func (lua *LuaProvider) EnsureResolutionMatches(L *lua.LState) int {
	lua.provider.EnsureResolutionMatches(L.CheckUserData(1).Value.(*gocv.Mat))
	return 0
}

// GetCurrentPage wrapper for lua engine
func (lua *LuaProvider) GetCurrentPage(L *lua.LState) int {
	lua.provider.GetCurrentPage(L.CheckUserData(1).Value.(*gocv.Mat))
	return 0
}

// GuidedMode wrapper for lua engine
func (lua *LuaProvider) GuidedMode(L *lua.LState) int {
	lua.provider.GuidedMode()
	return 0
}

// ImgToString wrapper for lua engine
func (lua *LuaProvider) ImgToString(L *lua.LState) int {
	lua.provider.ImgToString()
	return 0
}

// IsProcessRunning wrapper for lua engine
func (lua *LuaProvider) IsProcessRunning(L *lua.LState) int {
	lua.provider.IsProcessRunning()
	return 0
}

// KillProcess wrapper for lua engine
func (lua *LuaProvider) KillProcess(L *lua.LState) int {
	lua.provider.KillProcess()
	return 0
}

// MethodName wrapper for lua engine
func (lua *LuaProvider) MethodName(L *lua.LState) int {
	lua.provider.MethodName()
	return 0
}

// PassThroughInitialScreen wrapper for lua engine
func (lua *LuaProvider) PassThroughInitialScreen(L *lua.LState) int {
	lua.provider.PassThroughInitialScreen()
	return 0
}

// PossibleBattlePoints wrapper for lua engine
func (lua *LuaProvider) PossibleBattlePoints(L *lua.LState) int {
	lua.provider.PossibleBattlePoints()
	return 0
}

// Scan wrapper for lua engine
func (lua *LuaProvider) Scan(L *lua.LState) int {
	lua.provider.Scan()
	return 0
}

// ScanForClose wrapper for lua engine
func (lua *LuaProvider) ScanForClose(L *lua.LState) int {
	lua.provider.ScanForClose()
	return 0
}

// ScanForOk wrapper for lua engine
func (lua *LuaProvider) ScanForOk(L *lua.LState) int {
	lua.provider.ScanForOk()
	return 0
}

// SpecialEvents wrapper for lua engine
func (lua *LuaProvider) SpecialEvents(L *lua.LState) int {
	lua.provider.SpecialEvents(L.CheckUserData(1).Value.(DuelLinksInstanceInfo))
	return 0
}

// StartProcess wrapper for lua engine
func (lua *LuaProvider) StartProcess(L *lua.LState) int {
	lua.provider.StartProcess()
	return 0
}

// Swipe wrapper for lua engine
func (lua *LuaProvider) Swipe(L *lua.LState) int {
	lua.provider.Swipe(L.CheckInt(1), L.CheckInt(2), L.CheckInt(3), L.CheckInt(4))
	return 0
}

// SwipeRight wrapper for lua engine
func (lua *LuaProvider) SwipeRight(L *lua.LState) int {
	lua.provider.SwipeRight(L.CheckInt(1))
	return 0
}

// SwipeTime wrapper for lua engine
func (lua *LuaProvider) SwipeTime(L *lua.LState) int {
	lua.provider.SwipeTime(L.CheckInt(1), L.CheckInt(2), L.CheckInt(3), L.CheckInt(4), L.CheckInt(5))
	return 0
}

// SystemCall wrapper for lua engine
func (lua *LuaProvider) SystemCall(L *lua.LState) int {
	lua.provider.SystemCall()
	return 0
}

// TakePNGScreenShot wrapper for lua engine
func (lua *LuaProvider) TakePNGScreenShot(L *lua.LState) int {
	lua.provider.TakePNGScreenShot()
	return 0
}

// Tap wrapper for lua engine
func (lua *LuaProvider) Tap(L *lua.LState) int {
	lua.provider.Tap(L.CheckInt(1), L.CheckInt(2))
	return 0
}

// VerifyBattle wrapper for lua engine
func (lua *LuaProvider) VerifyBattle(L *lua.LState) int {
	lua.provider.VerifyBattle()
	return 0
}

// WaitFor wrapper for lua engine
func (lua *LuaProvider) WaitFor(L *lua.LState) int {
	lua.provider.WaitFor()
	return 0
}

// WaitForAutoDuel wrapper for lua engine
func (lua *LuaProvider) WaitForAutoDuel(L *lua.LState) int {
	lua.provider.WaitForAutoDuel()
	return 0
}

// WaitForUi wrapper for lua engine
func (lua *LuaProvider) WaitForUi(L *lua.LState) int {
	lua.provider.WaitForUi(L.CheckInt(1))
	return 0
}

// WaitForWhiteBottom wrapper for lua engine
func (lua *LuaProvider) WaitForWhiteBottom(L *lua.LState) int {
	lua.provider.WaitForWhiteBottom()
	return 0
}
