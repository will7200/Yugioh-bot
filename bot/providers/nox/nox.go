package nox

import (
	"bufio"
	"context"
	"encoding/base64"
	"fmt"
	"image"
	"strconv"
	"strings"
	"time"

	"github.com/ahmetb/go-linq"
	"github.com/mitchellh/go-ps"
	"github.com/pkg/errors"
	"github.com/spf13/afero"
	"github.com/will7200/Yugioh-bot/bot/base"
	"github.com/will7200/Yugioh-bot/bot/dl"
	"github.com/zach-klippenstein/goadb"
	"gocv.io/x/gocv"
)

var (
	log             = base.CheckWithSourcedLog().With("package", "bot.provider.nox")
	takeImage       = []string{"screencap", "-p"}
	takeBase64Image = append(takeImage, []string{"|", "busybox", "base64"}...)
)

func init() {
	dl.RegisterProvider("Nox", NewNoxProvider)
}

type NoxProvider struct {
	dl.Provider
	noxPath             string
	device              *adb.Device
	client              *adb.Adb
	options             *dl.Options
	predefined          *dl.Predefined
	imageCaptureCommand []string
	dimensions          image.Point
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
		log.Panic("Could not find the nox executable")
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
		y, err = base.GetInt(args[1])
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

func (nox *NoxProvider) Swipe(args ...interface{}) {
	var px1, py1, px2, py2 int
	var err error
	switch t := args[0].(type) {
	case dl.UILocation:
		if len(args) != 2 {
			log.Panic("Using dl.UILocation requires two parameters")
		}
		p2, ok := args[1].(dl.UILocation)
		if !ok {
			log.Panic(err)
		}
		px1, py1 = t.Point.X, t.Point.Y
		px2, py2 = p2.Point.X, p2.Point.Y
	case image.Point:
		if len(args) != 2 {
			log.Panic("Using image.Point requires two parameters")
		}
		p2, ok := args[1].(image.Point)
		if !ok {
			log.Panic(err)
		}
		px1, py1 = t.X, t.Y
		px2, py2 = p2.X, p2.Y
	case int:
		if len(args) != 4 {
			log.Panic("Using int requires four parameters")
		}
		var ok, ok2, ok3 bool
		py1, ok = args[1].(int)
		px2, ok2 = args[2].(int)
		py2, ok3 = args[3].(int)
		if !ok || !ok2 || !ok3 {
			log.Panic("Could not convert the remaining parameters to int")
		}
	default:
		log.Panicf("Swipe: type %T", t)
	}
	log.Debug(fmt.Sprintf("Swiping from (%d, %d) to (%d, %d)", px1, py1, px2, py2))
	noxArgs := strings.Split(fmt.Sprintf("%d %d %d %d", px1, py1, px2, py2), " ")
	noxArgs = append([]string{"swipe"}, noxArgs...)
	_, err = nox.device.RunCommand("input", noxArgs...)
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
	result, err := nox.device.RunCommand(takeBase64Image[0], takeBase64Image[1:]...)
	if err != nil {
		return &dl.PreCheckError{Reason: err}
	}
	scanner := bufio.NewScanner(strings.NewReader(result))
	if scanner.Scan() {
		if !strings.Contains(scanner.Text(), "not found") {
			log.Info("Android Device has busybox using base64 encoder")
			nox.imageCaptureCommand = takeBase64Image
		} else {
			log.Warn("Android Device does not have busybox note image transfer may be slows")
			nox.imageCaptureCommand = takeImage
		}
	}
	dims := nox.GetScreenDimensions()
	log.Infof("Using device with %dx%d screen size", dims.X, dims.Y)
	return nil
}

func (nox *NoxProvider) TakePNGScreenShot() ([]byte, error) {
	result, err := nox.device.RunCommand(nox.imageCaptureCommand[0], nox.imageCaptureCommand[1:]...)
	if err != nil {
		return nil, err
	}
	if len(nox.imageCaptureCommand) == len(takeImage) {
		return []byte(result), nil
	}
	img, err := base64.StdEncoding.DecodeString(result)
	return img, err
}

func (nox *NoxProvider) startApp() error {
	_, err := nox.device.RunCommand("monkey", "-p", "jp.konami.duellinks", "-c", "android.intent.category.LAUNCHER", "1")
	if err != nil {
		return err
	}
	return nil
}

func (nox *NoxProvider) getImage(key string, tryDefault bool) (gocv.Mat, error) {
	var asset dl.AssetMap
	asset = nox.GetAsset(key)
	if asset.Key == "" && tryDefault {
		asset = nox.predefined.GetAsset("Asset-" + dl.TransformKey(key, dl.DefaultSize))
	}
	if asset.Key == "" {
		log.Panicf("Asset resource %s does not have a mapping", key)
	}
	original, err := dl.OpenUIAsset(asset.Name, nox.options.HomeDir, nox.options.FileSystem)
	if err != nil {
		return gocv.Mat{}, err
	}
	b, err := afero.ReadAll(original)
	original.Close()
	if err != nil {
		return gocv.Mat{}, err
	}
	imgMat, err := gocv.IMDecode(b, gocv.IMReadGrayScale)
	if imgMat.Empty() || err != nil {
		return imgMat, fmt.Errorf("Matrix is empty for resource %s", key)
	}
	if tryDefault {
		resizedImage := gocv.NewMat()
		gocv.Resize(imgMat, &resizedImage, nox.dimensions, 0, 0, gocv.InterpolationNearestNeighbor)
		imgMat.Close()
		return resizedImage, nil
	}
	return imgMat, nil

}

func (nox *NoxProvider) isStartScreen() bool {
	imgMat, err := nox.getImage("start_screen", true)
	if err != nil {
		log.Panic("Cannot make comparision against the open page, missing a start_screen asset")
	}
	against := nox.GetImgFromScreenShot(false, 1)
	if !base.CVEqualDim(imgMat, against) {
		log.Panic("Cannot compare two images that are not the same dimensions")
	}
	grayedMat := base.CvtColor(against, gocv.ColorBGRToGray)
	against.Close()

	if gocv.CountNonZero(grayedMat) == 0 {
		grayedMat.Close()
		imgMat.Close()
		return false
	}

	lb := base.NewMatSCScalar(140)
	ub := base.NewMatSCScalar(255)
	maskedMat := base.MaskImage(grayedMat, lb, ub, true)
	maskedOriginal := base.MaskImage(imgMat, lb, ub, true)

	imgMat.Close()
	grayedMat.Close()

	lb.Close()
	ub.Close()

	defer maskedOriginal.Close()
	defer maskedMat.Close()
	score := base.SSIM_GOCV(maskedMat, maskedOriginal)
	log.Debugf("Start Screen Similarity: %.2f vs %.2f", score, nox.predefined.BotConst.StartScreenSimilarity)
	if score > nox.predefined.BotConst.StartScreenSimilarity {
		return true
	}
	return false
}

func (nox *NoxProvider) InitialScreen(started bool) (bool, error) {
	if err := nox.startApp(); err != nil {
		return false, err
	}
	if started {
		log.Info("Checking for start screen")
		ct := context.WithValue(context.Background(), "panicWait", 1*time.Second)
		ct = context.WithValue(ct, "onFalseCondition", 500*time.Millisecond)
		ctx, cancel := context.WithTimeout(ct, 5*time.Second)
		defer cancel()
		homeScreen, err := dl.GenericWaitFor(ctx,
			nox, "DuelLinks Landing Page", func(i interface{}) bool {
				return i.(bool)
			}, func(i map[string]interface{}) interface{} {
				return nox.isStartScreen()
			}, map[string]interface{}{})
		if err != nil {
			return false, err
		}
		if !homeScreen {
			return false, nil
		}
	}
	ct := context.WithValue(context.Background(), "panicWait", 1*time.Second)
	ct = context.WithValue(ct, "onFalseCondition", 500*time.Millisecond)
	ctx, cancel := context.WithTimeout(ct, 20*time.Second)
	defer cancel()
	homeScreen, err := dl.GenericWaitFor(ctx,
		nox, "DuelLinks Landing Page", func(i interface{}) bool {
			return i.(bool)
		}, func(i map[string]interface{}) interface{} {
			return nox.isStartScreen()
		}, map[string]interface{}{})
	if err != nil {
		log.Error("Error occurred while waiting for home screen")
		return false, err
	}
	if !homeScreen {
		log.Warn("No home screen detected")
		return false, nil
	}
	//log.Info("Passing through start screen")
	//nox.Tap(nox.GetUILocation("initiate_link"))
	return true, nil
}

func (nox *NoxProvider) GetScreenDimensions() image.Point {
	message, err := nox.device.RunCommand("wm", "size")
	if err != nil {
		log.Panic(err)
	}
	sizeMessage := strings.TrimSpace(strings.SplitAfter(message, ":")[1])
	if strings.Contains(sizeMessage, "x") {
		size := strings.Split(sizeMessage, "x")
		if len(size) != 2 {
			log.Panic("Size dimension is not len of 2 cannot parse")
		}
		width, err := strconv.Atoi(size[0])
		if err != nil {
			log.Panic("Cannot parse dimensions")
		}
		height, err := strconv.Atoi(size[1])
		if err != nil {
			log.Panic("Cannot parse dimensions")
		}
		nox.dimensions = image.Pt(width, height)
		return nox.dimensions
	}
	log.Panic("Cannot parse dimensions")
	return image.Pt(0, 0)
}

func (nox *NoxProvider) ScreenDimensions() image.Point {
	return nox.dimensions
}

func NewNoxProvider(o *dl.Options) dl.Provider {
	np := &NoxProvider{
		Provider: dl.NewBaseProvider(o),
		noxPath:  o.Path,
	}
	np.options = o
	np.predefined = o.Predefined
	o.Provider = np
	return np
}
