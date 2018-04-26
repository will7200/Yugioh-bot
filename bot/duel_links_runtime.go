package bot

import (
	"fmt"
	"os"
	"path"
	"time"

	"github.com/mitchellh/go-homedir"
	"github.com/pelletier/go-toml"
	log2 "github.com/prometheus/common/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/afero"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/will7200/Yugioh-bot/bot/providers"
	"github.com/yuin/gopher-lua"
)

const (
	botRunOnStartUp         = "bot.RunOnStartUp"
	botKillProviderOnFinish = "bot.KillProviderOnFinish"
	botSleepFactor          = "bot.SleepFactor"
	botPersistenceType      = "bot.PersistenceType"
	botPersistenceLocation  = "bot.PersistenceLocation"
)

var (
	playModesRegistered = map[PlayMode]*lua.LFunction{}
	log                 = base.CheckWithSourcedLog().With("package", "bot")
	luaLog              = log2.NewPassedLoggerUnsourced(logrus.StandardLogger()).With("from", "lua")
)

func init() {
	base.RegisterExecutor("main", func(job *base.Job) (interface{}, error) {
		rt := job.Args["rt"].(*runTime)
		err := rt.Main()
		if err != nil {
			log.Error(err)
		}
		return nil, err
	})
}

type PlayMode string

type ErrInvalidPlayMode struct {
	m string
}

func (err *ErrInvalidPlayMode) Error() string {
	return fmt.Sprintf("Playmode %s is not registered", err.m)
}

func RegisterPlayMode(mode string, fun *lua.LFunction) {
	playModesRegistered[PlayMode(mode)] = fun
}

func GetPlayMode(mode string) (PlayMode, error) {
	if _, ok := playModesRegistered[PlayMode(mode)]; ok {
		return PlayMode(mode), nil
	}
	return PlayMode(""), &ErrInvalidPlayMode{mode}
}

type RunTimeOptions struct {
	Active    bool
	LastRunAt time.Time
	NextRunAt time.Time
	RunNow    bool
	Stop      bool
	PlayMode  PlayMode
}

type BotOptions struct {
	KillProviderOnFinish bool
	RunOnStartUp         bool
	SleepFactor          float64
	PersistenceLocation  string
	PersistenceType      string
}

type BotConfig struct {
	Title string
	Bot   BotOptions `toml:"bot"`
}

type RunTime interface {
	Start() error
	Main() error
	SetUp() error
	HandleOptionChange(name string, value interface{})
	GetProvider() providers.Provider
}

type runTime struct {
	options    RunTimeOptions
	rtOptions  BotOptions
	fs         afero.Fs
	dispatcher *base.Dispatcher
	provider   providers.Provider
	mainJob    *base.Job
}

func (rt *runTime) Start() error {
	if rt.rtOptions.RunOnStartUp {
		rt.options.NextRunAt = time.Now().Add(1 * time.Second)
	} else {
		rt.scheduleNextRunTime()
	}
	err := rt.provider.PreCheck()
	if err != nil {
		log.Error("Prechecks failed")
		log.Fatal(err)
	}
	if rt.mainJob == nil {
		j := base.NewJob("Duel Links Main", "main", "PT4H",
			-1, map[string]interface{}{"rt": rt})
		j.Init(rt.dispatcher)
	}
	return nil
}

func (rt *runTime) Main() error {
	rt.options.Active = true
	rt.options.LastRunAt = time.Now()
	provider := rt.GetProvider()
	if isRunning := provider.IsProcessRunning(); !isRunning {
		provider.StartProcess()
		provider.WaitForUi(30)
	}
	home, err := homedir.Expand(base.HomeDir)
	if err != nil {
		return err
	}
	file, err := rt.fs.Open(path.Join(home, "lua", "entrypoint.lua"))
	if err != nil {
		return err
	}
	os.Setenv("LUA_PATH", path.Join(home, "lua")+string(os.PathSeparator)+"?.lua;")
	L := lua.NewState(lua.Options{})
	defer L.Close()
	L.PreloadModule("provider", providers.ProviderLoader(rt.provider))
	L.PreloadModule("register", Loader)
	L.SetGlobal("luaprint", L.NewFunction(luaPrint))
	if err := L.DoFile(file.Name()); err != nil {
		log.Error(err)
	}
	return nil
}

func luaPrint(L *lua.LState) int {
	args := make([]interface{}, L.GetTop())
	for i := 1; i <= L.GetTop(); i++ {
		args[i-1] = L.Get(i)
	}
	if base.CheckIfDebug() {
		if debug, ok := L.GetStack(1); ok {
			L.GetInfo("l", debug, lua.LNil)
			L.GetInfo("S", debug, lua.LNil)
			if debug.Source == "" {
				luaLog.Info(args...)
				return 0
			}
			luaLog.With("source", debug.Source).With("line", debug.CurrentLine).Info(args...)
			return 0
		}
	}
	luaLog.Info(args...)
	return 0
}

func (rt *runTime) scheduleNextRunTime() {
	if rt.options.NextRunAt.IsZero() {
		rt.options.NextRunAt = time.Now().Add(5 * time.Second)
	} else if time.Now().After(rt.options.NextRunAt) {
		rt.options.NextRunAt = time.Now().Add(5 * time.Second)
	}
}

func (rt *runTime) SetUp() error {
	log.Panic("implement me")
	return nil
}

func (rt *runTime) HandleOptionChange(name string, value interface{}) {
	log.Panic("implement me")
}

func (rt *runTime) GetProvider() providers.Provider {
	return rt.provider
}

func NewRunTime(d *base.Dispatcher, provider providers.Provider) RunTime {
	appfs := base.NewFSFromName("os")
	config := BotConfig{}
	file, err := appfs.Open(viper.ConfigFileUsed())
	if err != nil {
		log.Fatal(err)
	}
	tree, err := toml.LoadReader(file)
	if err != nil {
		log.Fatal(err)
	}
	err = tree.Unmarshal(&config)
	if err != nil {
		log.Fatal(err)
	}
	botOptions := config.Bot
	options, fs := readPersistanceFile(&botOptions)
	return &runTime{
		rtOptions:  botOptions,
		options:    options,
		fs:         fs,
		dispatcher: d,
		provider:   provider,
	}
}

func readPersistanceFile(botOptions *BotOptions) (RunTimeOptions, afero.Fs) {
	rtfs := base.NewFSFromName(botOptions.PersistenceType)
	file, err := rtfs.Open(botOptions.PersistenceLocation)
	if err != nil {
		file, _ = rtfs.Create(botOptions.PersistenceLocation)
	}
	rtp := RunTimeOptions{}
	tree, err := toml.LoadReader(file)
	if err != nil {
		log.Error("Couldn't read persistence file due to:", err)
		return rtp, rtfs
	}
	tree.Unmarshal(&rtp)
	return rtp, rtfs
}
