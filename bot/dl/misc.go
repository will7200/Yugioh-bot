package dl

import (
	"image"

	"gocv.io/x/gocv"
)

const (
	AssetPrefix         = "Asset-"
	UILocationPrefix    = "UILocation-"
	LocationPrefix      = "Location-"
	AreaLocationPrefeix = "AreaLocation-"
)

// Miscellaneous all functions that don't fall under actions or are bot specific
// fall under here
type Miscellaneous interface {
	IsProcessRunning() bool
	StartProcess()
	KillProcess()
	EnsureResolutionMatches(mat *gocv.Mat)
	// Ensures that every is ok
	PreCheck() error
	ScreenDimensions() image.Point
	GetAsset(key string) AssetMap
	GetUILocation(key string) UILocation
	GetLocation(key string) Location
	GetAreaLocation(key string) AreaLocation
}

type BaseMiscellaneous struct {
	options    *Options
	predefined *Predefined
}

func (bm *BaseMiscellaneous) ScreenDimensions() image.Point {
	return bm.options.Provider.ScreenDimensions()
}

func (bm *BaseMiscellaneous) GetAsset(key string) AssetMap {
	return bm.predefined.GetAsset(AssetPrefix + TransformKey(key, bm.ScreenDimensions()))
}

func (bm *BaseMiscellaneous) GetUILocation(key string) UILocation {
	return bm.predefined.GetUILocation(UILocationPrefix + TransformKey(key, bm.ScreenDimensions()))
}

func (bm *BaseMiscellaneous) GetLocation(key string) Location {
	return bm.predefined.GetLocation(LocationPrefix + TransformKey(key, bm.ScreenDimensions()))
}

func (bm *BaseMiscellaneous) GetAreaLocation(key string) AreaLocation {
	return bm.predefined.GetAreaLocation(AreaLocationPrefeix + TransformKey(key, bm.ScreenDimensions()))
}

func (*BaseMiscellaneous) PreCheck() error {
	log.Panic("implement me")
	return nil
}

func (*BaseMiscellaneous) IsProcessRunning() bool {
	//log.Panic("implement me")
	return true
}

func (*BaseMiscellaneous) StartProcess() {
	log.Panic("implement me")
}

func (*BaseMiscellaneous) KillProcess() {
	log.Panic("implement me")
}

func (*BaseMiscellaneous) EnsureResolutionMatches(mat *gocv.Mat) {
	log.Panic("implement me")
}

func NewMisc(o *Options) Miscellaneous {
	bm := BaseMiscellaneous{}
	bm.options = o
	bm.predefined = o.Predefined
	misc := DuelLinksMisc{bm}
	fallBackMisc := WithFallBackMiscellaneous(&misc, o.Predefined, image.Pt(480, 800))
	return fallBackMisc
}

type fallBackMiscellaneous struct {
	defaultDimensions image.Point
	delegate          Miscellaneous
	predefined        *Predefined
	resize            Resizer
}

func (fb *fallBackMiscellaneous) IsProcessRunning() bool {
	return fb.delegate.IsProcessRunning()
}

func (fb *fallBackMiscellaneous) StartProcess() {
	fb.delegate.StartProcess()
}

func (fb *fallBackMiscellaneous) KillProcess() {
	fb.delegate.KillProcess()
}

func (fb *fallBackMiscellaneous) EnsureResolutionMatches(mat *gocv.Mat) {
	fb.delegate.EnsureResolutionMatches(mat)
}

func (fb *fallBackMiscellaneous) PreCheck() error {
	return fb.delegate.PreCheck()
}

func (fb *fallBackMiscellaneous) ScreenDimensions() image.Point {
	return fb.delegate.ScreenDimensions()
}

func (fb *fallBackMiscellaneous) GetAsset(key string) AssetMap {
	asset := fb.delegate.GetAsset(key)
	if asset == (AssetMap{}) {
		return fb.predefined.GetAsset(AssetPrefix + TransformKey(key, fb.defaultDimensions))
	}
	return asset
}

func (fb *fallBackMiscellaneous) GetUILocation(key string) UILocation {
	asset := fb.delegate.GetUILocation(key)
	if asset == (UILocation{}) {
		dims := fb.delegate.ScreenDimensions()
		asset = fb.predefined.GetUILocation(UILocationPrefix + TransformKey(key, fb.defaultDimensions))
		nasset, err := fb.resize.Resize(asset, &dims)
		if err != nil {
			log.Panic(err)
		}
		return nasset.(UILocation)
	}
	return asset
}

func (fb *fallBackMiscellaneous) GetLocation(key string) Location {
	asset := fb.delegate.GetLocation(key)
	if asset == (Location{}) {
		return fb.predefined.GetLocation(LocationPrefix + TransformKey(key, fb.defaultDimensions))
	}
	return asset
}

func (fb *fallBackMiscellaneous) GetAreaLocation(key string) AreaLocation {
	asset := fb.delegate.GetAreaLocation(key)
	if asset == (AreaLocation{}) {
		return fb.predefined.GetAreaLocation(AreaLocationPrefeix + TransformKey(key, fb.defaultDimensions))
	}
	return asset
}

func WithFallBackMiscellaneous(misc Miscellaneous, predefined *Predefined, defaultDims image.Point) Miscellaneous {
	fbm := fallBackMiscellaneous{delegate: misc, defaultDimensions: defaultDims, predefined: predefined}
	fbm.resize = NewResizer(defaultDims)
	return &fbm
}
