package dl

import (
	"time"

	"runtime"

	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/yuin/gopher-lua"
	"gocv.io/x/gocv"
)

// ProviderLoader loads all exposed provider methods
func ProviderLoader(provider Provider) func(*lua.LState) int {
	return func(L *lua.LState) int {
		_ = L.NewTypeMetatable("dl.Location")
		_ = L.NewTypeMetatable("dl.UILocation")
		_ = L.NewTypeMetatable("image.Point")
		_ = L.NewTypeMetatable("[]uint8")
		_ = L.NewTypeMetatable("dl.AreaLocation")
		_ = L.NewTypeMetatable("dl.AssetMap")
		_ = L.NewTypeMetatable("gocv.Mat")
		luaProvider := NewLuaProvider(provider)
		exports := map[string]lua.LGFunction{
			"battle":                     luaProvider.Battle,
			"battle_mode":                luaProvider.BattleMode,
			"check_battle":               luaProvider.CheckBattle,
			"check_if_battle":            luaProvider.CheckIfBattle,
			"determine_auto_duel_status": luaProvider.DetermineAutoDuelStatus,
			"ensure_resolution_matches":  luaProvider.EnsureResolutionMatches,
			"get_area_location":          luaProvider.GetAreaLocation,
			"get_asset":                  luaProvider.GetAsset,
			"get_current_page":           luaProvider.GetCurrentPage,
			"get_img_from_screen_shot":   luaProvider.GetImgFromScreenShot,
			"get_location":               luaProvider.GetLocation,
			"get_ui_location":            luaProvider.GetUILocation,
			"guided_mode":                luaProvider.GuidedMode,
			"img_to_string":              luaProvider.ImgToString,
			"is_process_running":         luaProvider.IsProcessRunning,
			"kill_process":               luaProvider.KillProcess,
			"initial_screen":             luaProvider.InitialScreen,
			"possible_battle_points":     luaProvider.PossibleBattlePoints,
			"pre_check":                  luaProvider.PreCheck,
			"scan":                       luaProvider.Scan,
			"scan_for":                   luaProvider.ScanFor,
			"screen_dimensions":          luaProvider.ScreenDimensions,
			"special_events":             luaProvider.SpecialEvents,
			"start_process":              luaProvider.StartProcess,
			"swipe":                      luaProvider.Swipe,
			"swipe_right":                luaProvider.SwipeRight,
			"swipe_time":                 luaProvider.SwipeTime,
			"system_call":                luaProvider.SystemCall,
			"take_png_screen_shot":       luaProvider.TakePNGScreenShot,
			"tap":           luaProvider.Tap,
			"verify_battle": luaProvider.VerifyBattle,
			"wait_for":      luaProvider.WaitFor,
			"wait_for_ui":   luaProvider.WaitForUi,
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

// Battle wrapper for lua engine
func (lp *LuaProvider) Battle(L *lua.LState) int {
	lp.provider.Battle()
	return 0
}

// BattleMode wrapper for lua engine
func (lp *LuaProvider) BattleMode(L *lua.LState) int {
	lp.provider.BattleMode(L.CheckString(1), L.CheckString(2), L.CheckString(3))
	return 0
}

// CheckBattle wrapper for lua engine
func (lp *LuaProvider) CheckBattle(L *lua.LState) int {
	lp.provider.CheckBattle()
	return 0
}

// CheckIfBattle wrapper for lua engine
func (lp *LuaProvider) CheckIfBattle(L *lua.LState) int {
	lp.provider.CheckIfBattle()
	return 0
}

// DetermineAutoDuelStatus wrapper for lua engine
func (lp *LuaProvider) DetermineAutoDuelStatus(L *lua.LState) int {
	lp.provider.DetermineAutoDuelStatus()
	return 0
}

// EnsureResolutionMatches wrapper for lua engine
func (lp *LuaProvider) EnsureResolutionMatches(L *lua.LState) int {
	lp.provider.EnsureResolutionMatches(L.CheckUserData(1).Value.(*gocv.Mat))
	return 0
}

// GetAreaLocation wrapper for lua engine
func (lp *LuaProvider) GetAreaLocation(L *lua.LState) int {
	A := lp.provider.GetAreaLocation(L.CheckString(1))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("dl.AreaLocation"))
	L.Push(userDefinedA)
	return 1
}

// GetAsset wrapper for lua engine
func (lp *LuaProvider) GetAsset(L *lua.LState) int {
	A := lp.provider.GetAsset(L.CheckString(1))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("dl.AssetMap"))
	L.Push(userDefinedA)
	return 1
}

// GetCurrentPage wrapper for lua engine
func (lp *LuaProvider) GetCurrentPage(L *lua.LState) int {
	lp.provider.GetCurrentPage(L.CheckUserData(1).Value.(*gocv.Mat))
	return 0
}

// GetImgFromScreenShot wrapper for lua engine
func (lp *LuaProvider) GetImgFromScreenShot(L *lua.LState) int {
	A := lp.provider.GetImgFromScreenShot(L.CheckBool(1), L.CheckInt(2))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	runtime.SetFinalizer(&A, base.FreeMat)
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("gocv.Mat"))
	L.Push(userDefinedA)
	return 1
}

// GetLocation wrapper for lua engine
func (lp *LuaProvider) GetLocation(L *lua.LState) int {
	A := lp.provider.GetLocation(L.CheckString(1))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("dl.Location"))
	L.Push(userDefinedA)
	return 1
}

// GetUILocation wrapper for lua engine
func (lp *LuaProvider) GetUILocation(L *lua.LState) int {
	A := lp.provider.GetUILocation(L.CheckString(1))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("dl.UILocation"))
	L.Push(userDefinedA)
	return 1
}

// GuidedMode wrapper for lua engine
func (lp *LuaProvider) GuidedMode(L *lua.LState) int {
	lp.provider.GuidedMode()
	return 0
}

// ImgToString wrapper for lua engine
func (lp *LuaProvider) ImgToString(L *lua.LState) int {
	lp.provider.ImgToString()
	return 0
}

// IsProcessRunning wrapper for lua engine
func (lp *LuaProvider) IsProcessRunning(L *lua.LState) int {
	A := lp.provider.IsProcessRunning()
	L.Push(lua.LBool(A))
	return 1
}

// KillProcess wrapper for lua engine
func (lp *LuaProvider) KillProcess(L *lua.LState) int {
	lp.provider.KillProcess()
	return 0
}

// InitialScreen wrapper for lua engine
func (lp *LuaProvider) InitialScreen(L *lua.LState) int {
	A, B := lp.provider.InitialScreen(L.CheckBool(1))
	if B != nil {
		L.Push(lua.LBool(A))
		L.Push(lua.LString(B.Error()))
		return 1
	}
	L.Push(lua.LBool(A))
	return 1
}

// PossibleBattlePoints wrapper for lua engine
func (lp *LuaProvider) PossibleBattlePoints(L *lua.LState) int {
	lp.provider.PossibleBattlePoints()
	return 0
}

// PreCheck wrapper for lua engine
func (lp *LuaProvider) PreCheck(L *lua.LState) int {
	A := lp.provider.PreCheck()
	L.Push(lua.LString(A.Error()))
	return 1
}

// Scan wrapper for lua engine
func (lp *LuaProvider) Scan(L *lua.LState) int {
	lp.provider.Scan()
	return 0
}

// ScanFor wrapper for lua engine
func (lp *LuaProvider) ScanFor(L *lua.LState) int {
	lp.provider.ScanFor()
	return 0
}

// ScreenDimensions wrapper for lua engine
func (lp *LuaProvider) ScreenDimensions(L *lua.LState) int {
	A := lp.provider.ScreenDimensions()
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("image.Point"))
	L.Push(userDefinedA)
	return 1
}

// SpecialEvents wrapper for lua engine
func (lp *LuaProvider) SpecialEvents(L *lua.LState) int {
	lp.provider.SpecialEvents(L.CheckUserData(1).Value.(DuelLinksInstanceInfo))
	return 0
}

// StartProcess wrapper for lua engine
func (lp *LuaProvider) StartProcess(L *lua.LState) int {
	lp.provider.StartProcess()
	return 0
}

// Swipe wrapper for lua engine
func (lp *LuaProvider) Swipe(L *lua.LState) int {
	lp.provider.Swipe(L.CheckInt(1), L.CheckInt(2), L.CheckInt(3), L.CheckInt(4))
	return 0
}

// SwipeRight wrapper for lua engine
func (lp *LuaProvider) SwipeRight(L *lua.LState) int {
	lp.provider.SwipeRight(L.CheckInt(1))
	return 0
}

// SwipeTime wrapper for lua engine
func (lp *LuaProvider) SwipeTime(L *lua.LState) int {
	lp.provider.SwipeTime(L.CheckInt(1), L.CheckInt(2), L.CheckInt(3), L.CheckInt(4), L.CheckInt(5))
	return 0
}

// SystemCall wrapper for lua engine
func (lp *LuaProvider) SystemCall(L *lua.LState) int {
	lp.provider.SystemCall()
	return 0
}

// TakePNGScreenShot wrapper for lua engine
func (lp *LuaProvider) TakePNGScreenShot(L *lua.LState) int {
	A, B := lp.provider.TakePNGScreenShot()
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	L.SetMetatable(userDefinedA, L.GetTypeMetatable("[]uint8"))
	L.Push(userDefinedA)
	if B == nil {
		return 1
	}
	L.Push(lua.LString(B.Error()))
	return 2
}

// Tap wrapper for lua engine
func (lp *LuaProvider) Tap(L *lua.LState) int {
	args := make([]interface{}, L.GetTop())
	for i := 1; i <= L.GetTop(); i++ {
		if lv, ok := L.Get(i).(*lua.LUserData); ok {
			args[i-1] = lv.Value
			continue
		}
		args[i-1] = L.Get(i)
	}
	lp.provider.Tap(args...)
	return 0
}

// VerifyBattle wrapper for lua engine
func (lp *LuaProvider) VerifyBattle(L *lua.LState) int {
	lp.provider.VerifyBattle()
	return 0
}

// WaitFor wrapper for lua engine
func (lp *LuaProvider) WaitFor(L *lua.LState) int {
	lp.provider.WaitFor()
	return 0
}

// WaitForUi wrapper for lua engine
func (lp *LuaProvider) WaitForUi(L *lua.LState) int {
	lp.provider.WaitForUi(time.Duration(L.CheckInt(1)) * time.Second)
	return 0
}

// ComparatorLoader loads all exposed comparator methods
func ComparatorLoader(comparator Comparator) func(*lua.LState) int {
	return func(L *lua.LState) int {
		luaComparator := NewLuaComparator(comparator)
		exports := map[string]lua.LGFunction{"compare": luaComparator.Compare}
		mod := L.SetFuncs(L.NewTable(), exports)
		L.SetField(mod, "name", lua.LString("comparator"))
		L.Push(mod)
		return 1
	}
}

// LuaComparator methods exposed in lua engine
type LuaComparator struct {
	comparator Comparator
}

// NewLuaComparator returns a lua provider instance
func NewLuaComparator(comparator Comparator) *LuaComparator {
	return &LuaComparator{comparator: comparator}
}

// Compare wrapper for lua engine
func (lp *LuaComparator) Compare(L *lua.LState) int {
	v := L.Get(3)
	var corr Correlation
	if intv, ok := v.(lua.LNumber); ok {
		corr = Correlation(int(intv))
	} else {
		corr = L.CheckUserData(3).Value.(Correlation)
	}
	A := lp.comparator.Compare(L.CheckString(1), L.CheckUserData(2).Value.(gocv.Mat), corr)
	L.Push(lua.LBool(A))
	return 1
}
