package main

import (
	"fmt"
	"reflect"
	"strconv"

	"strings"

	. "github.com/dave/jennifer/jen"
	"github.com/will7200/Yugioh-bot/bot/dl"
	"github.com/will7200/Yugioh-bot/gen/lib"
)

const (
	detectorLoader = "DetectorLoader"
	detector       = "LuaDetector"
)

func luadetector() *File {
	f := NewFile("dl")
	f.ImportAlias(gopherLua, "lua")
	f.ImportName("gocv.io/x/gocv", "gocv")
	registeredImports := map[string]string{
		"gocv": "gocv.io/x/gocv",
	}
	f.Commentf("%s loads all exposed detector methods", detectorLoader)
	mapFunctions := Dict{}
	luaDetector := "luaDetector"
	funcLoaderProvider := make([]Code, 6)
	funcLoaderProvider = append(funcLoaderProvider, []Code{
		Id(luaDetector).Op(":=").Id("NewLuaDetector").Params(Id("detector")),
		Id("exports").Op(":=").Map(String()).Qual(gopherLua, "LGFunction").Values(
			mapFunctions,
		),
		Id("mod").Op(":=").Id("L").Op(".").Id("SetFuncs").Params(Id("L").Op(".").Id("NewTable").Call(), Id("exports")),
		Id("L").Op(".").Id("SetField").Params(Id("mod"), Lit("name"), Qual(gopherLua, "LString").Params(Lit("detector"))),
		Id("L").Op(".").Id("Push").Params(Id("mod")),
		Return(Lit(1)),
	}...)
	loaderDetector := f.Func().Id(detectorLoader).Params(Id("detector").Id("Detector")).Id(
		"func(*lua.LState) int",
	)
	f.Commentf("%s methods exposed in lua engine", detector)
	f.Type().Id(detector).Struct(
		Id("detector").Id("Detector"),
	)
	f.Comment("NewLuaDetector returns a lua provider instance")
	f.Func().Id("NewLuaDetector").Params(Id("detector").Id("Detector")).Op("*").Id("LuaDetector").Block(
		Return(
			Op("&").Id("LuaDetector").Values(
				Id("detector").Op(":").Id("detector"),
			),
		),
	)
	detector2 := dl.NewDetector(&dl.Options{})
	fooType := reflect.TypeOf(detector2)
	setTypes := make(map[string]struct{})
	for i := 0; i < fooType.NumMethod(); i++ {
		method := fooType.Method(i)
		fmt.Println(lib.Split(method.Name))
		t := Id("lp.detector." + method.Name)
		mapFunctions[Lit(strings.ToLower(strings.Join(lib.Split(method.Name), "_")))] = Id(luaDetector).Op(".").Id(method.Name)
		paramsArray := make([]Code, method.Type.NumIn()-1)
		for j := 1; j < method.Type.NumIn(); j++ {
			l := method.Type.In(j)
			arg := strings.Replace(l.String(), impersonate+".", "", 1)
			var paraType *Statement
			paraType = Id(arg)
			if strings.Contains(arg, ".") {
				pack := strings.Split(strings.Replace(arg, "*", "", 1), ".")[0]
				if strings.Contains(arg, "*") {
					paraType = Op("*").Qual(registeredImports[pack], strings.Split(arg, ".")[1])
				} else {
					paraType = Qual(registeredImports[pack], strings.Split(arg, ".")[1])
				}
			}

			callFunction := (func(arg string) *Statement {
				lFunc := "L.Check"
				addInterface := false
				switch arg {
				case "int":
					lFunc += "Int"
				case "int64":
					lFunc += "Int64"
				case "string":
					lFunc += "String"
				case "bool":
					lFunc += "Bool"
				default:
					lFunc += "UserData"
					addInterface = true
				}
				statement := Id(lFunc).Params(Id(strconv.Itoa(j)))
				if addInterface {
					statement.Op(".").Id("Value").Op(".").Params(paraType)
				}
				return statement
			})(arg)
			paramsArray = append(paramsArray, callFunction)
		}
		o := Empty()
		//pa := make([]string, method.Type.NumOut())
		retPush := make([]Code, method.Type.NumOut()+2)
		if method.Type.NumOut() > 0 {
			fmt.Println("output")
			for j := 0; j < method.Type.NumOut(); j++ {
				returnName := method.Type.Out(j).String()
				retName := string('A' + j)
				o.Id(retName)
				lPushArea := make([]Code, 1)
				lPush := Id("L").Dot("Push")
				switch {
				case strings.Contains(returnName, "error"):
					lPush.Params(Qual(gopherLua, "LString").Params(Id(retName).Dot("Error").Call()))
				case strings.Contains(returnName, "bool"):
					lPush.Params(Qual(gopherLua, "LBool").Params(Id(retName)))
				case strings.Contains(returnName, "string"):
					lPush.Params(Qual(gopherLua, "LString").Params(Id(retName)))
				default:
					setTypes[returnName] = struct{}{}
					lPushArea = append(lPushArea, []Code{
						Id("userDefined" + retName).Op(":=").Id("L").Dot("NewUserData").Call(),
						Id("userDefined" + retName).Dot("Value").Op("=").Id(retName),
						Id("L").Dot("SetMetatable").Params(
							Id("userDefined"+retName), Id("L").Dot("GetTypeMetatable").Params(Lit(returnName)),
						),
					}...)
					lPush.Params(Id("userDefined" + retName))
				}
				lPushArea = append(lPushArea, lPush)
				retPush = append(retPush, lPushArea...)
				if j != (method.Type.NumOut() - 1) {
					o.Op(",")
				}
			}
			o.Op(":=")
		}
		retPush = append([]Code{o}, retPush...)
		retPush = append(retPush, Return(Lit(method.Type.NumOut())))
		o.Add(t.Params(paramsArray...))
		f.Commentf("%s wrapper for lua engine", method.Name)
		f.Func().Params(
			Id("lp").Op("*").Id(detector),
		).Id(method.Name).Params(
			Id("L").Op("*").Qual(gopherLua, "LState"),
		).Int().Block(retPush...)
	}
	newSetTypes := make([]Code, len(setTypes))
	if len(setTypes) > 0 {
		for sT := range setTypes {
			fmt.Println(sT)
			newSetTypes = append(newSetTypes, Id("_").Op("=").Id("L").Dot("NewTypeMetatable").Call(Lit(sT)))
		}
	}
	funcLoaderProvider = append(newSetTypes, funcLoaderProvider...)
	loaderDetector.Block(
		Return(
			Func().Params(Id("L").Op("*").Qual(gopherLua, "LState")).Int().Block(
				funcLoaderProvider...,
			),
		),
	)
	return f
}
