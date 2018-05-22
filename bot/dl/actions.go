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
	Swipe(x1, y1, x2, y2 int)
	SwipeTime(x1, y1, x2, y2, timeAmount int)
	SwipeRight(timeSleep int)
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

func (action *BaseActions) Swipe(x1, y1, x2, y2 int) {
	log.Panic("implement me")
}

func (action *BaseActions) SwipeTime(x1, y1, x2, y2, timeAmount int) {
	log.Panic("implement me")
}

func (action *BaseActions) SwipeRight(timeSleep int) {
	log.Panic("implement me")
}

func (action *BaseActions) WaitForUi(timeSleep time.Duration) {
	log.Debugf("Sleep for %.2f seconds", timeSleep.Seconds()*action.options.SleepFactor)
	time.Sleep(time.Duration(int64(float64(timeSleep.Nanoseconds()) * action.options.SleepFactor)))
}

func (action *BaseActions) GetImgFromScreenShot(fromCache bool, fail int) gocv.Mat {
	if lastImage, found := action.cache.Get(LastImage); found && fromCache {
		return lastImage.(gocv.Mat)
	} else if found {
		img := lastImage.(gocv.Mat)
		if !img.Empty() {
			img.Close()
		}
	}
	action.cache.DeleteExpired()
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
		img := gocv.IMDecode(screenShot, gocv.IMReadColor)
		if img.Empty() {
			continue
		}
		action.cache.Set(LastImage, img.Clone(), cache.DefaultExpiration)
		return img
	}
	log.Panicf("Cannot obtain proper image for provider")
	return gocv.NewMat()
}

// NewActions
func NewActions(o *Options) Actions {
	action := new(BaseActions)
	action.cache = o.ImageCache
	action.options = o
	return action
}
