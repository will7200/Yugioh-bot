package bot

import (
	"fmt"
	"os"
	"path"
	"runtime"
	"runtime/debug"
	"strconv"
	"time"

	"github.com/cenkalti/backoff"
	"github.com/pelletier/go-toml"
	log2 "github.com/prometheus/common/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/afero"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/will7200/Yugioh-bot/bot/dl"
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
	currentMode         = PlayMode("")
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

func (p *PlayMode) String() string {
	return string(*p)
}

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

func AvailableModes() []string {
	var playModes []string
	for key := range playModesRegistered {
		playModes = append(playModes, key.String())
	}
	return playModes
}

func SetMode(mode string) error {
	pb, err := GetPlayMode(mode)
	if err != nil {
		return err
	}
	currentMode = pb
	log.Infof("Mode change: %v", currentMode)
	return nil
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
	GetProvider() dl.Provider
	SetChan(chan struct{})
	SetDetector(o dl.Detector)
}

type runTime struct {
	options    RunTimeOptions
	rtOptions  BotOptions
	fs         afero.Fs
	appfs      afero.Fs
	dispatcher *base.Dispatcher
	provider   dl.Provider
	detector   dl.Detector
	mainJob    *base.Job
	signal     chan struct{}
	homedir    string
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
		log.Panic(err)
	}
	if rt.mainJob == nil {
		j := base.NewJob("Duel Links Main", "main", "PT1S",
			-1, map[string]interface{}{"rt": rt})
		b := backoff.NewExponentialBackOff()
		b.MaxElapsedTime = time.Hour * 1
		b.InitialInterval = time.Second * 10
		b.MaxInterval = time.Minute * 30
		bf := backoff.WithMaxRetries(b, 10)
		j.BackOff = bf
		j.Init(rt.dispatcher)
	}
	return nil
}

func (rt *runTime) Main() error {
	defer func() {
		if r := recover(); r != nil {
			log.Errorf("%v", r)
			fmt.Print(string(debug.Stack()))
			rt.signal <- struct{}{}
		}
	}()
	rt.options.Active = true
	rt.options.LastRunAt = time.Now()
	file, err := rt.appfs.Open(path.Join(rt.homedir, "lua", "entrypoint.lua"))
	if err != nil {
		return err
	}
	os.Setenv("LUA_PATH", path.Join(rt.homedir, "lua")+string(os.PathSeparator)+"?.lua;")
	L := lua.NewState(lua.Options{})
	defer L.Close()
	L.PreloadModule("provider", dl.ProviderLoader(rt.provider))
	L.PreloadModule("rt", RunTimeLoader(rt))
	L.PreloadModule("detector", dl.DetectorLoader(rt.detector))
	L.PreloadModule("common", dl.CommonLoader(rt.provider.Options()))
	L.SetGlobal("luaprint", L.NewFunction(luaPrint))
	file.Close()
	if err := L.DoFile(file.Name()); err != nil {
		return err
	}
	runtime.GC()
	debug.FreeOSMemory()
	return nil
}

func luaPrint(L *lua.LState) int {
	args := make([]interface{}, L.GetTop())
	for i := 1; i <= L.GetTop(); i++ {
		args[i-1] = L.Get(i)
	}
	if base.CheckIfDebug() {
		if debug2, ok := L.GetStack(1); ok {
			L.GetInfo("l", debug2, lua.LNil)
			L.GetInfo("S", debug2, lua.LNil)
			if debug2.Source == "" {
				luaLog.Info(args...)
				return 0
			}
			lineNumber := strconv.Itoa(debug2.CurrentLine)
			luaLog.With("source", debug2.Source+":"+lineNumber).Info(args...)
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

func (rt *runTime) GetProvider() dl.Provider {
	return rt.provider
}

func (rt *runTime) SetChan(o chan struct{}) {
	rt.signal = o
}

func (rt *runTime) SetDetector(o dl.Detector) {
	rt.detector = o
}

func NewRunTime(d *base.Dispatcher, provider dl.Provider, home string, appfs afero.Fs) RunTime {
	config := BotConfig{}
	file, err := appfs.Open(viper.ConfigFileUsed())
	if err != nil {
		log.Panic(err)
	}
	tree, err := toml.LoadReader(file)
	if err != nil {
		log.Panic(err)
	}
	err = tree.Unmarshal(&config)
	if err != nil {
		log.Panic(err)
	}
	botOptions := config.Bot
	options, fs := readPersistenceFile(&botOptions)
	return &runTime{
		rtOptions:  botOptions,
		options:    options,
		fs:         fs,
		appfs:      appfs,
		homedir:    home,
		dispatcher: d,
		provider:   provider,
	}
}

func readPersistenceFile(botOptions *BotOptions) (RunTimeOptions, afero.Fs) {
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
