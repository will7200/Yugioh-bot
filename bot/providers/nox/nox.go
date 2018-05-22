package nox

import (
	"github.com/will7200/Yugioh-bot/bot/providers"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/zach-klippenstein/goadb"
	"github.com/pkg/errors"
	"encoding/base64"
	"github.com/mitchellh/go-ps"
	"github.com/ahmetb/go-linq"
	"strings"
)

var (
	log             = base.CheckWithSourcedLog().With("package", "bot.provider.nox")
	takeBase64Image = []string{"screencap", "-p", "|", "busybox", "base64"}
)

func init() {
	providers.RegisterProvider("Nox", NewNoxProvider)
}

type NoxProvider struct {
	providers.Provider
	noxPath string
	device  *adb.Device
	client  *adb.Adb
	options *providers.Options
}

// IsProcessRunning this function is practically useless now that I think is about for the Nox provider at least
// adb will fail the program if not vm is attached to, keep now for legacy reasons
func (nox *NoxProvider) IsProcessRunning() bool {
	// I am making the assumptions that the remote is current not managed by the local machine
	// If it does happen that the remote process is not running then adb will capture that error
	// either on the device watch or when it execute a command
	if nox.options.IsRemote {
		return true
	}
	processes, err := ps.Processes()
	if err != nil {
		log.Panic(err)
	}
	process := linq.From(processes).Where(func(p interface{}) bool {
		return strings.Contains(strings.ToLower(p.(ps.Process).Executable()), "nox app player") ||
			strings.Contains(strings.ToLower(p.(ps.Process).Executable()), "nox.exe")
	}).First()
	if process == nil {
		log.Fatal("Could not find the nox executable")
		return false
	}
	switch process.(type) {
	case ps.Process:
		return true
	default:
		return false
	}
	return false
}

func (nox *NoxProvider) Tap(args ...interface{}) {
	if len(args) < 1 {
		log.Panic("Tap: requires at minimum one arguments")
	}
	var x, y int
	var err error
	switch t := args[0].(type) {
	case dl.UILocation:
		x = t.Point.X
		y = t.Point.Y

	case int:
		if len(args) != 2 {
			log.Panic("Tap: int type requires two arguments to be passed")
		}
		x, err = base.GetInt(t)
		if err != nil {
			log.Panic(err)
		}
		y, err = base.GetInt(t)
		if err != nil {
			log.Panic(err)
		}
	default:
		log.Panicf("Tap: type %T", t)
	}
	log.Debug(fmt.Sprintf("Tapping at %d, %d", x, y))
	_, err = nox.device.RunCommand("input", "tap", fmt.Sprintf("%d", x), fmt.Sprintf("%d", y))
	if err != nil {
		log.Panic(err)
	}
}

func (nox *NoxProvider) SetClientDevice(client *adb.Adb, device adb.DeviceDescriptor) {
	nox.client = client
	nox.device = client.Device(device)
}

func (nox *NoxProvider) PreCheck() error {
	if nox.device.String() == "" {
		return errors.New("Android Device Is Null")
	}
	return nil
}

func (nox *NoxProvider) TakePNGScreenShot() ([]byte, error) {
	result, err := nox.device.RunCommand("screencap", "-p", "|", "busybox", "base64")
	if err != nil {
		return nil, err
	}
	img, err := base64.StdEncoding.DecodeString(result)
	return img, err
}

func NewNoxProvider(o *providers.Options) providers.Provider {
	np := &NoxProvider{
		Provider: providers.NewBaseProvider(o),
		noxPath:  o.Path,
	}
	np.options = o
	o.Provider = np
	return np
}
