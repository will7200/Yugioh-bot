package main

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"

	. "github.com/dave/jennifer/jen"
	"github.com/will7200/Yugioh-bot/bot/providers"
	"github.com/will7200/Yugioh-bot/gen/lib"
)

func luaprovider() *File {
	f := NewFile("providers")
	f.ImportAlias(gopherLua, "lua")
	f.ImportName("gocv.io/x/gocv", "gocv")
	registeredImports := map[string]string{
		"gocv": "gocv.io/x/gocv",
	}
	f.Commentf("%s loads all exposed provider methods", loader)
	mapFunctions := Dict{}
	luaProvider := "luaProvider"
	f.Func().Id(loader).Params(Id("provider").Id("Provider")).Id(
		"func(*lua.LState) int",
	).Block(
		Return(
			Func().Params(Id("L").Op("*").Qual(gopherLua, "LState")).Int().Block(
				Id(luaProvider).Op(":=").Id("NewLuaProvider").Params(Id("provider")),
				Id("exports").Op(":=").Map(String()).Qual(gopherLua, "LGFunction").Values(
					mapFunctions,
				),
				Id("mod").Op(":=").Id("L").Op(".").Id("SetFuncs").Params(Id("L").Op(".").Id("NewTable").Call(), Id("exports")),
				Id("L").Op(".").Id("SetField").Params(Id("mod"), Lit("name"), Qual(gopherLua, "LString").Params(Lit("provider"))),
				Id("L").Op(".").Id("Push").Params(Id("mod")),
				Return(Lit(1)),
			),
		),
	)
	f.Commentf("%s methods exposed in lua engine", provider)
	f.Type().Id(provider).Struct(
		Id("provider").Id("Provider"),
	)
	f.Comment("NewLuaProvider returns a lua provider instance")
	f.Func().Id("NewLuaProvider").Params(Id("provider").Id("Provider")).Op("*").Id("LuaProvider").Block(
		Return(
			Op("&").Id("LuaProvider").Values(
				Id("provider").Op(":").Id("provider"),
			),
		),
	)
	provider := providers.NewBaseProvider(&providers.Options{})
	fooType := reflect.TypeOf(provider)
	for i := 0; i < fooType.NumMethod(); i++ {
		method := fooType.Method(i)
		fmt.Println(lib.Split(method.Name))
		t := Id("lua.provider." + method.Name)
		mapFunctions[Lit(strings.ToLower(strings.Join(lib.Split(method.Name), "_")))] = Id(luaProvider).Op(".").Id(method.Name)
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
		t.Params(paramsArray...)
		f.Commentf("%s wrapper for lua engine", method.Name)
		f.Func().Params(
			Id("lua").Id("*LuaProvider"),
		).Id(method.Name).Params(
			Id("L").Op("*").Qual(gopherLua, "LState"),
		).Int().Block(
			t,
			Return(Id("0")),
		)
	}
	return f
}
