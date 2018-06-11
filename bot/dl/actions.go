package dl

import (
	"image"
	"time"

	"github.com/patrickmn/go-cache"
	"gocv.io/x/gocv"
)

const (
	LastImage = "LAST-IMAGE"
)

// Actions
type Actions interface {
	Tap(args ...interface{})
	Swipe(args ...interface{})
	SwipeTime(args ...interface{})
	WaitForUi(timeSleep time.Duration)
	TakePNGScreenShot() ([]byte, error)
	GetImgFromScreenShot(fromCache bool, fail int) gocv.Mat
}

// BaseActions
type BaseActions struct {
	cache            *cache.Cache
	provider         Provider
	predefined       *Predefined
	options          *Options
	resizeDimensions image.Point
}

func (action *BaseActions) TakePNGScreenShot() ([]byte, error) {
	panic("error")
}

func (action *BaseActions) Tap(args ...interface{}) {
	log.Panic("implement me")
}

func (action *BaseActions) Swipe(args ...interface{}) {
	log.Panic("implement me")
}

func (action *BaseActions) SwipeTime(args ...interface{}) {
	log.Panic("implement me")
}

func (action *BaseActions) WaitForUi(timeSleep time.Duration) {
	// log.Debugf("Sleep for %.2f seconds", timeSleep.Seconds()*action.options.Predefined.BotConst.SleepFactor)
	time.Sleep(time.Duration(int64(float64(timeSleep.Nanoseconds()) * action.options.Predefined.BotConst.SleepFactor)))
}

func (action *BaseActions) GetImgFromScreenShot(fromCache bool, fail int) gocv.Mat {
	if lastImage, found := action.cache.Get(LastImage); found && fromCache {
		return lastImage.(gocv.Mat)
	}
	for timesFailed := 0; timesFailed < fail; timesFailed++ {
		// I am cheating here really not a good design pattern
		// Since go will call BaseActions implementation of TakePNGScreenShot
		// When the provider method is not implemented again
		// This way no rewrites are necessary but again bad, so will probably change
		screenShot, err := action.options.Provider.TakePNGScreenShot()
		if err != nil {
			log.Error(err)
			continue
		}
		img, err := gocv.IMDecode(screenShot, gocv.IMReadColor)
		if img.Empty() || err != nil {
			continue
		}
		go func() {
			if lastImage, found := action.cache.Get(LastImage); found {
				lt := lastImage.(gocv.Mat)
				lt.Close()
			}
			action.cache.Set(LastImage, img, cache.DefaultExpiration)
		}()
		return img.Clone()
	}
	log.Panicf("Cannot obtain proper image for provider")
	return gocv.NewMat()
}

// NewActions
func NewActions(o *Options) Actions {
	action := new(BaseActions)
	action.cache = o.ImageCache
	action.options = o
	ticker := time.NewTicker(5 * time.Minute)
	go func() {
		for t := range ticker.C {
			log.Debug("Cleaning cache at %s", t.Format(time.RFC3339))
			action.cache.DeleteExpired()
		}
	}()
	return action
}
