package dl

import (
	"image"
	"time"

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
			"ensure_resolution_matches": luaProvider.EnsureResolutionMatches,
			"get_area_location":         luaProvider.GetAreaLocation,
			"get_asset":                 luaProvider.GetAsset,
			"get_img_from_screen_shot":  luaProvider.GetImgFromScreenShot,
			"get_location":              luaProvider.GetLocation,
			"get_ui_location":           luaProvider.GetUILocation,
			"is_process_running":        luaProvider.IsProcessRunning,
			"kill_process":              luaProvider.KillProcess,
			"initial_screen":            luaProvider.InitialScreen,
			"pre_check":                 luaProvider.PreCheck,
			"scan_for":                  luaProvider.ScanFor,
			"screen_dimensions":         luaProvider.ScreenDimensions,
			"special_events":            luaProvider.SpecialEvents,
			"start_process":             luaProvider.StartProcess,
			"swipe":                     luaProvider.Swipe,
			"swipe_time":                luaProvider.SwipeTime,
			"take_png_screen_shot":      luaProvider.TakePNGScreenShot,
			"tap":         luaProvider.Tap,
			"wait_for":    luaProvider.WaitFor,
			"wait_for_ui": luaProvider.WaitForUi,
		}
		mod := L.SetFuncs(L.NewTable(), exports)
		L.SetField(mod, "name", lua.LString("provider"))
		options := L.NewUserData()
		options.Value = provider.Options()
		L.SetField(mod, "options", options)
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

// GetImgFromScreenShot wrapper for lua engine
func (lp *LuaProvider) GetImgFromScreenShot(L *lua.LState) int {
	A := lp.provider.GetImgFromScreenShot(L.CheckBool(1), L.CheckInt(2))
	userDefinedA := L.NewUserData()
	userDefinedA.Value = A
	// runtime.SetFinalizer(&A, base.FreeMat)
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

// PreCheck wrapper for lua engine
func (lp *LuaProvider) PreCheck(L *lua.LState) int {
	A := lp.provider.PreCheck()
	L.Push(lua.LString(A.Error()))
	return 1
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
	args := make([]interface{}, L.GetTop())
	for i := 1; i <= L.GetTop(); i++ {
		if lv, ok := L.Get(i).(*lua.LUserData); ok {
			args[i-1] = lv.Value
			continue
		}
		args[i-1] = L.CheckInt(i)
	}
	lp.provider.Swipe(args...)
	return 0
}

// SwipeTime wrapper for lua engine
func (lp *LuaProvider) SwipeTime(L *lua.LState) int {
	lp.provider.SwipeTime(L.CheckInt(1), L.CheckInt(2), L.CheckInt(3), L.CheckInt(4), L.CheckInt(5))
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
		args[i-1] = L.CheckInt(i)
	}
	lp.provider.Tap(args...)
	return 0
}

// WaitFor wrapper for lua engine
func (lp *LuaProvider) WaitFor(L *lua.LState) int {
	lp.provider.WaitFor()
	return 0
}

// WaitForUi wrapper for lua engine
func (lp *LuaProvider) WaitForUi(L *lua.LState) int {
	sleep := float64(L.CheckNumber(1))
	if sleep < 1 {
		lp.provider.WaitForUi(time.Duration(sleep*1000) * time.Millisecond)
		return 0
	}
	lp.provider.WaitForUi(time.Duration(sleep) * time.Second)
	return 0
}

const (
	circleType      = "dl.Circle"
	arrayCircleType = "[]dl.Circle"
)

// DetectorLoader loads all exposed detector methods
func DetectorLoader(detector Detector) func(*lua.LState) int {
	return func(L *lua.LState) int {
		_ = L.NewTypeMetatable(arrayCircleType)
		circle := L.NewTypeMetatable(circleType)
		L.SetField(circle, "__type", lua.LString(circleType))
		L.SetField(circle, "__index", L.SetFuncs(L.NewTable(), circleMethods))
		luaDetector := NewLuaDetector(detector)
		exports := map[string]lua.LGFunction{
			"circles": luaDetector.Circles,
			"compare": luaDetector.Compare,
		}
		mod := L.SetFuncs(L.NewTable(), exports)
		L.SetField(mod, "name", lua.LString("detector"))
		L.Push(mod)
		return 1
	}
}

// LuaDetector methods exposed in lua engine
type LuaDetector struct {
	detector Detector
}

// NewLuaDetector returns a lua provider instance
func NewLuaDetector(detector Detector) *LuaDetector {
	return &LuaDetector{detector: detector}
}

func checkCircle(L *lua.LState) *Circle {
	ud := L.CheckUserData(1)
	if v, ok := ud.Value.(Circle); ok {
		return &v
	}
	L.ArgError(1, "array of circles expected")
	return nil
}

// Getter and setter for the circle#Point
func circleGetSetPoint(L *lua.LState) int {
	p := checkCircle(L)
	if L.GetTop() == 3 {
		p.Point = image.Pt(L.CheckInt(2), L.CheckInt(3))
		return 0
	}
	L.Push(lua.LNumber(p.Point.X))
	L.Push(lua.LNumber(p.Point.Y))
	return 2
}

// Getter and setter for the circle#Radius
func circleGetSetRadius(L *lua.LState) int {
	p := checkCircle(L)
	if L.GetTop() == 2 {
		p.Radius = L.CheckInt(2)
		return 0
	}
	L.Push(lua.LNumber(p.Radius))
	return 1
}

var circleMethods = map[string]lua.LGFunction{
	"point":  circleGetSetPoint,
	"radius": circleGetSetRadius,
}

// Circles wrapper for lua engine
func (lp *LuaDetector) Circles(L *lua.LState) int {
	A, B := lp.detector.Circles(L.CheckString(1), L.CheckUserData(2).Value.(gocv.Mat))
	luaCircles := L.NewTable()
	for _, value := range A {
		userDefined := L.NewUserData()
		userDefined.Value = value
		L.SetMetatable(userDefined, L.GetTypeMetatable(circleType))
		luaCircles.Append(userDefined)
	}
	L.SetMetatable(luaCircles, L.GetTypeMetatable(arrayCircleType))
	L.Push(luaCircles)
	L.Push(lua.LBool(B))
	return 2
}

// Compare wrapper for lua engine
func (lp *LuaDetector) Compare(L *lua.LState) int {
	v := L.Get(3)
	var corr Correlation
	if intv, ok := v.(lua.LNumber); ok {
		corr = Correlation(int(intv))
	} else {
		corr = L.CheckUserData(3).Value.(Correlation)
	}
	A := lp.detector.Compare(L.CheckString(1), L.CheckUserData(2).Value.(gocv.Mat), corr)
	L.Push(lua.LBool(A))
	return 1
}

// Common functions exposed in lua engine
func CommonLoader(options *Options) func(*lua.LState) int {
	return func(L *lua.LState) int {
		exports := map[string]lua.LGFunction{
			"check_if_battle": checkIfBattle(options),
			"is_start_screen": isStartScreen(options),
		}
		mod := L.SetFuncs(L.NewTable(), exports)
		L.SetField(mod, "name", lua.LString("common"))
		L.Push(mod)
		return 1
	}
}

func checkIfBattle(options *Options) func(*lua.LState) int {
	return func(L *lua.LState) int {
		A, B := CheckIfBattle(
			L.CheckUserData(1).Value.(gocv.Mat),
			float64(L.CheckNumber(2)),
			*options,
		)
		if B != nil {
			L.Push(lua.LBool(A))
			L.Push(lua.LString(B.Error()))
			return 2
		}
		L.Push(lua.LBool(A))
		return 1
	}
}

func isStartScreen(options *Options) func(*lua.LState) int {
	return func(L *lua.LState) int {
		A, B := IsStartScreen(
			L.CheckUserData(1).Value.(gocv.Mat),
			*options,
		)
		if B != nil {
			L.Push(lua.LBool(A))
			L.Push(lua.LString(B.Error()))
			return 2
		}
		L.Push(lua.LBool(A))
		return 1
	}
}
