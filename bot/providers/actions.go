package providers

import (
	"gocv.io/x/gocv"
	"github.com/patrickmn/go-cache"
	"github.com/adelowo/onecache"
	"time"
	"fmt"
)

var store onecache.Store

const (
	LAST_IMAGE = "LAST-IMAGE"
)

type Actions interface {
	Tap(x, y int)
	Swipe(x1, y1, x2, y2 int)
	SwipeTime(x1, y1, x2, y2, timeAmount int)
	SwipeRight(timeSleep int)
	WaitForUi(timeSleep int)
	TakePNGScreenShot() ([]byte, error)
	GetImgFromScreenShot(fromCache bool, fail int) gocv.Mat
}

type BaseActions struct {
	cache    *cache.Cache
	options  *Options
	provider Provider
}

func (action *BaseActions) TakePNGScreenShot() ([]byte, error) {
	fmt.Println(action.cache)
	panic("error")
}

func (action *BaseActions) Tap(x, y int) {
	panic("implement me")
}

func (action *BaseActions) Swipe(x1, y1, x2, y2 int) {
	panic("implement me")
}

func (action *BaseActions) SwipeTime(x1, y1, x2, y2, timeAmount int) {
	panic("implement me")
}

func (action *BaseActions) SwipeRight(timeSleep int) {
	panic("implement me")
}

func (action *BaseActions) WaitForUi(timeSleep int) {
	time.Sleep(time.Duration(int64(timeSleep)) * time.Second)
}

func (action *BaseActions) GetImgFromScreenShot(fromCache bool, fail int) gocv.Mat {
	if lastImage, found := action.cache.Get(LAST_IMAGE); found && fromCache {
		return lastImage.(gocv.Mat)
	}
	for timesFailed := 0; timesFailed < fail; timesFailed++ {
		// I am cheating here really not a good design pattern
		// Since go will call BaseActions implementation of TakePNGScreenShot
		// When the provider method is not implemented again
		// This way no rewrites are necessary but again bad, so will probably change
		screenShot, err := action.provider.TakePNGScreenShot()
		if err != nil {
			continue
		}
		img := gocv.IMDecode(screenShot, gocv.IMReadColor)
		if img.Empty() {
			continue
		}
		action.cache.Set(LAST_IMAGE, img, cache.DefaultExpiration)
		return img
	}
	log.Fatal("Cannot obtain proper image for provider")
	return gocv.Mat{}
}

func NewActions(o *Options) Actions {
	cache := cache.New(5*time.Minute, 10*time.Minute)
	action := new(BaseActions)
	action.cache = cache
	action.options = o
	action.provider = o.Provider
	return action
}
