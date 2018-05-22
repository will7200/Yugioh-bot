package dl

import (
	"context"
	"fmt"

	"errors"

	"runtime/debug"

	"path"

	"time"

	"github.com/emirpasic/gods/sets/hashset"
	"github.com/patrickmn/go-cache"
	"github.com/sirupsen/logrus"
	"github.com/spf13/afero"
	"github.com/will7200/Yugioh-bot/bot/base"
	"gocv.io/x/gocv"
)

var (
	log       = base.CheckWithSourcedLog().With("package", "bot.base")
	providers = map[string]NewProvider{}
)

// Options
type Options struct {
	Path        string
	HomeDir     string
	SleepFactor float64
	IsRemote    bool

	Provider   Provider
	Predefined *Predefined
	FileSystem afero.Fs
	Dispatcher *base.Dispatcher
	ImageCache *cache.Cache
}

// OpenUIAsset
func OpenUIAsset(name, home string, appfs afero.Fs) (afero.File, error) {
	f, err := appfs.Open(GetUIPath(name, home))
	return f, err
}

// GetUIPath
func GetUIPath(name, home string) string {
	if path.IsAbs(name) {
		return name
	}
	return path.Join(home, "assets", name)
}

// GetImageFromAsset
func GetImageFromAsset(asset AssetMap, options Options) (gocv.Mat, error) {
	original, err := OpenUIAsset(asset.Name, options.HomeDir, options.FileSystem)
	if err != nil {
		return gocv.Mat{}, err
	}
	b, err := afero.ReadAll(original)
	original.Close()
	if err != nil {
		return gocv.Mat{}, err
	}
	imgMat := gocv.IMDecode(b, gocv.IMReadGrayScale)
	if imgMat.Empty() {
		return imgMat, fmt.Errorf("Matrix is empty for resource %s", asset.Name)
	}
	return imgMat, nil
}

func TryImageFromCache(asset AssetMap, options Options, c *cache.Cache) (gocv.Mat, error) {
	if image, found := c.Get(asset.Key); found {
		return image.(gocv.Mat), nil
	}
	image, err := GetImageFromAsset(asset, options)
	if err != nil {
		return image, err
	}
	c.Add(asset.Key, image, cache.DefaultExpiration)
	return image, nil
}

// NewProvider
type NewProvider func(options *Options) Provider

func RegisterProvider(name string, value NewProvider) {
	providers[name] = value
}

func GetProvider(name string, options *Options) Provider {
	if val, ok := providers[name]; ok {
		return val(options)
	}
	panic(fmt.Sprintf("Could not Get Provider %s", name))
	return nil
}

type PreCheckError struct {
	Reason error
}

func (e *PreCheckError) Error() string {
	return fmt.Sprintf("Precheck error. Reason: %s", e.Reason.Error())
}

// returns error only when returnError is specified
func GenericWaitFor(ctx context.Context, provider Provider, messeage string, checkCondition func(interface{}) bool,
	fn func(map[string]interface{}) interface{}, args map[string]interface{}) (bool, error) {
	log.Debug("Waiting for " + messeage)
	//timeout := GetDefault(args, "timeout", 10).(int)
	//returnError := GetDefault(args, "throw", true).(bool)
	tryAmount, ok := ctx.Value("tryAmount").(int)
	if !ok {
		tryAmount = 5
	}
	onPanicWait, ok := ctx.Value("panicWait").(time.Duration)
	if !ok {
		onPanicWait = time.Second * 1
	}
	onFalseCondition, ok := ctx.Value("onFalseCondition").(time.Duration)
	if !ok {
		onFalseCondition = time.Second * 2
	}
	attempts := 0
	set := hashset.New()
	errorSet := hashset.New()
	for {
		select {
		case <-ctx.Done():
			for index, val := range set.Values() {
				log.Debugf("Unique error %d", index)
				fmt.Println(val)
			}
			return false, nil
		default:
			if attempts >= tryAmount {
				for index, val := range set.Values() {
					log.Debugf("Unique error %d", index)
					fmt.Println(val)
				}
				return false, errors.New("Exceeded amount retries")
			}
			f := func() (con interface{}, failed bool) {
				defer func() {
					if r := recover(); r != nil {
						log.Debugf("Recovered in function for %s", messeage)
						switch v := r.(type) {
						case *logrus.Entry:
							if !errorSet.Contains(v.Message) {
								errorSet.Add(v.Message)
								if base.CheckIfDebug() {
									set.Add(string(debug.Stack()))
								}
							}
						}
						failed = true
						provider.WaitForUi(onPanicWait)
					}
				}()
				con = fn(args)
				return
			}
			condition, failed := f()
			attempts++
			if !failed && checkCondition(condition) {
				return true, nil
			}
			if !failed {
				provider.WaitForUi(onFalseCondition)
			}
		}
	}

}
