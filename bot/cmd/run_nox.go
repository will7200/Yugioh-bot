package cmd

import (
	"errors"
	"net/http"
	_ "net/http/pprof"
	"time"

	"github.com/ahmetb/go-linq"
	"github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/will7200/Yugioh-bot/bot"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/will7200/Yugioh-bot/bot/dl"
	"github.com/will7200/Yugioh-bot/bot/internal/controlserver"
	_ "github.com/will7200/Yugioh-bot/bot/providers/nox"
	nox2 "github.com/will7200/Yugioh-bot/bot/providers/nox"
	"github.com/will7200/Yugioh-bot/bot/rpc/control"
	"github.com/zach-klippenstein/goadb"
)

const (
	noxAdbHost     = "nox.adb-host"
	noxAdbPort     = "nox.adb-port"
	noxAdbLocation = "nox.adb-location"
	noxAdbDevice   = "nox.adb-device"
	noxAdbRemote   = "nox.adb-remote"
	noxAdbTimeout  = "nox.adb-timeout"
	noxPath        = "nox.path"
)

// botCmd represents the bot command
var botCmd = &cobra.Command{
	Use:   "nox",
	Short: "Start a bot instance using a nox instance",
	Long: `Starts the bot using nox as the emulator for Duel Links Bot. 
This is not limited to one instance, as long as the device is not in use by another bot instance.
Note if you are connecting to a remote adb instance, the local client and server must match versions.`,
	Run: noxInstance,
}

func init() {
	runCmd.AddCommand(botCmd)

	botCmd.Flags().String("adb-host", "", "adb server host name (defaults to localhost)")
	botCmd.Flags().Int("adb-port", 0, "adb server port (defaults to 5037)")
	botCmd.Flags().String("adb-location", "", "adb location on filesystem, include adb as well")
	botCmd.Flags().String("adb-device", "", "adb device name (cab be ip with port as well)")
	botCmd.Flags().Bool("adb-remote", false, "using a remote adb server so it nows how to start it if applicable")
	botCmd.Flags().Int("adb-timeout", 10, "timeout for adb to dial correctly")
	viper.BindPFlag(noxAdbHost, botCmd.Flag("adb-host"))
	viper.BindPFlag(noxAdbPort, botCmd.Flag("adb-port"))
	viper.BindPFlag(noxAdbLocation, botCmd.Flag("adb-location"))
	viper.BindPFlag(noxAdbDevice, botCmd.Flag("adb-device"))
	viper.BindPFlag(noxAdbRemote, botCmd.Flag("adb-remote"))
	viper.BindPFlag(noxAdbTimeout, botCmd.Flag("adb-timeout"))
}

type remoteStart struct {
}

func (t *remoteStart) Start() error {
	return errors.New("Remote Starting adb is not supported yet")
}

func noxInstance(cmd *cobra.Command, args []string) {
	if len(args) > 0 && args[0] == "client" {
		client()
		return
	}
	d := &base.Dispatcher{}
	d.StartDispatcher(viper.GetInt(botWorkers))
	rs := remoteStart{}
	client, err := adb.NewWithConfig(adb.ServerConfig{
		PathToAdb:    viper.GetString(noxAdbLocation),
		Host:         viper.GetString(noxAdbHost),
		Port:         viper.GetInt(noxAdbPort),
		Dialer:       adb.TcpDialerTimeout{Timeout: time.Second * time.Duration(viper.GetInt(noxAdbTimeout))},
		Remote:       viper.GetBool(noxAdbRemote),
		RemoteServer: adb.RemoteServer(&rs),
	})
	if err != nil {
		log.Error("Could not connect to the adb server")
		log.Error(err)
		log.Fatal("Try again")
	}
	devices, err := client.ListDevices()
	if err != nil {
		log.Fatal(err)
	}
	var device *adb.DeviceInfo
	if len(devices) == 0 {
		log.Fatal("No devices connected to adb server")
	}
	if len(devices) == 1 {
		device = devices[0]
	} else {
		var serialDevices []string
		linq.From(devices).Select(func(c interface{}) interface{} {
			return c.(*adb.DeviceInfo).Serial
		}).ToSlice(&serialDevices)
		log.Error("Need to choose a device since there is more than one connected")
		log.Errorf("Choose from %+v", serialDevices)
		log.Fatal("Re-run command with --adb-device={{ device name }}")
	}
	log.Infof("Using device %s", device.Serial)
	home, err := homedir.Expand(base.HomeDir)
	if err != nil {
		panic(err)
	}
	failure := make(chan struct{}, 1)
	list, err := base.GetListener(failure)
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		log.Warnln("Recovering socket from failure")
		list.Close()
	}()
	appfs := base.NewFSFromName("os")
	options := &dl.Options{
		Dispatcher:  d,
		IsRemote:    viper.GetBool(noxAdbRemote),
		SleepFactor: viper.GetFloat64(botSleepFactor),
		Path:        viper.GetString(noxPath),
		FileSystem:  appfs,
		HomeDir:     home,
		Predefined:  readDataFile(appfs),
		ImageCache:  base.NewImageCache(),
	}
	nox := dl.GetProvider("Nox", options)
	options.Provider = nox
	noxp := interface{}(nox).(*nox2.NoxProvider)
	noxp.SetClientDevice(client, adb.DeviceWithSerial(device.Serial))
	noxp.GetScreenDimensions()
	runTime := bot.NewRunTime(d, nox, home, appfs)
	runTime.SetChan(failure)
	runTime.SetComparator(dl.NewComparator(options))
	runTime.Start()

	server := controlserver.NewServer(bot.AvailableModes, bot.SetMode)
	twirpHandle := control.NewControlServer(server, nil)
	err = http.Serve(list, twirpHandle)
	if err != nil {
		log.Fatal(err)
	}
	log.Infoln("Exiting Now")
}
