package cmd

import (
	"github.com/spf13/cobra"
	"github.com/prometheus/common/log"
	"github.com/sirupsen/logrus"
	"os/signal"
	"os"
	"github.com/will7200/Yugioh-bot/bot/base"
	"fmt"
	"time"
	"os/exec"
	"github.com/zach-klippenstein/goadb"
	"io/ioutil"
)

var (
	client *adb.Adb
)
// botCmd represents the bot command
var botCmd = &cobra.Command{
	Use:   "nox",
	Short: "Starts the bot using a nox provider",
	Long:  `Starts the bot using nox as the emulator for Duel Links Bot`,
	Run: func(cmd *cobra.Command, args []string) {
		l := log.NewPassedLogger(logrus.StandardLogger())
		c := make(chan os.Signal, 1)
		signal.Notify(c, os.Interrupt)
		d := &base.Dispatcher{}
		d.StartDispatcher(4)
		j := &base.Job{Name: "Test", Epsilon: "PT5S", ID: "1", IsActive: true}
		j.Schedule = fmt.Sprintf("R/%s/PT2S", time.Now().Add(2 * time.Second).Format("2006-01-02T15:04:05Z-0700"))
		err := j.ParseSchedule()
		if err != nil {
			l.Errorln(err)
		}
		j.StartWaiting(d)
		newPath := os.Getenv("PATH")
		newPath += ":/Applications/Nox App Player.app/Contents/MacOS"
		os.Setenv("PATH", newPath)
		cmd1 := exec.Command("adb", "devices")
		cmd1.Stdout = os.Stdout
		cmd1.Stderr = os.Stderr
		cmd1.Env = append(os.Environ(),
			"FOO=duplicate_value", // ignored
			"FOO=actual_value",    // this value is used
		)
		//if err := cmd1.Run(); err != nil {
		//	l.Fatal(err)
		//}
		go t()
		//fmt.Println(binary)
		<-c
		l.Infoln("Exiting Now")
		os.Exit(1)
	},
}

func init() {
	runCmd.AddCommand(botCmd)

	botCmd.Flags().String("adb-host", "", "adb server host name (defaults to localhost)")
	botCmd.Flags().Int("adb-port", 0, "adb server port (defaults to 5037)")
	botCmd.Flags().String("adb-path", "", "adb")
}

func t() {
	var err error
	client, err = adb.NewWithConfig(adb.ServerConfig{PathToAdb: "/Users/williamflores/Downloads/platform-tools/adb", Host: "192.168.1.14"})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Starting server…")
	//client.StartServer()

	serverVersion, err := client.ServerVersion()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Server version:", serverVersion)

	devices, err := client.ListDevices()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Devices:")
	for _, device := range devices {
		fmt.Printf("\t%+v\n", *device)
	}

	serials, err := client.ListDeviceSerials()
	if err != nil {
		log.Fatal(err)
	}
	for _, serial := range serials {
		PrintDeviceInfoAndError(adb.DeviceWithSerial(serial))
	}

	fmt.Println()
	fmt.Println("Watching for device state changes.")
	watcher := client.NewDeviceWatcher()
	for event := range watcher.C() {
		fmt.Printf("\t[%s]%+v\n", time.Now(), event)
	}
	if watcher.Err() != nil {
		printErr(watcher.Err())
	}
}

func printErr(err error) {
	switch err := err.(type) {

	default:
		fmt.Println("error:", err)
	}
}

func PrintDeviceInfoAndError(descriptor adb.DeviceDescriptor) {
	device := client.Device(descriptor)
	if err := PrintDeviceInfo(device); err != nil {
		log.Error(err)
	}
}

func PrintDeviceInfo(device *adb.Device) error {
	serialNo, err := device.Serial()
	if err != nil {
		return err
	}
	devPath, err := device.DevicePath()
	if err != nil {
		return err
	}
	state, err := device.State()
	if err != nil {
		return err
	}

	fmt.Println(device)
	fmt.Printf("\tserial no: %s\n", serialNo)
	fmt.Printf("\tdevPath: %s\n", devPath)
	fmt.Printf("\tstate: %s\n", state)

	cmdOutput, err := device.RunCommand("pwd")
	if err != nil {
		fmt.Println("\terror running command:", err)
	}
	fmt.Printf("\tcmd output: %s\n", cmdOutput)

	stat, err := device.Stat("/sdcard")
	if err != nil {
		fmt.Println("\terror stating /sdcard:", err)
	}
	fmt.Printf("\tstat \"/sdcard\": %+v\n", stat)

	fmt.Println("\tfiles in \"/\":")
	entries, err := device.ListDirEntries("/")
	if err != nil {
		fmt.Println("\terror listing files:", err)
	} else {
		for entries.Next() {
			fmt.Printf("\t%+v\n", *entries.Entry())
		}
		if entries.Err() != nil {
			fmt.Println("\terror listing files:", err)
		}
	}

	fmt.Println("\tnon-existent file:")
	stat, err = device.Stat("/supercalifragilisticexpialidocious")
	if err != nil {
		fmt.Println("\terror:", err)
	} else {
		fmt.Printf("\tstat: %+v\n", stat)
	}

	fmt.Print("\tload avg: ")
	loadavgReader, err := device.OpenRead("/proc/loadavg")
	if err != nil {
		fmt.Println("\terror opening file:", err)
	} else {
		loadAvg, err := ioutil.ReadAll(loadavgReader)
		if err != nil {
			fmt.Println("\terror reading file:", err)
		} else {
			fmt.Println(string(loadAvg))
		}
	}

	return nil
}
