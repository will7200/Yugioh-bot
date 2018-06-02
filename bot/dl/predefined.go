package dl

import (
	"encoding/xml"
	"fmt"
	"image"
	"io"
	"os"
	"path"
	"strconv"

	"github.com/emirpasic/gods/trees/redblacktree"
	"github.com/gobuffalo/packr"
	"github.com/spf13/afero"
)

const (
	AssetPrefix         = "Asset-"
	UILocationPrefix    = "UILocation-"
	LocationPrefix      = "Location-"
	AreaLocationPrefeix = "AreaLocation-"
)

var (
	DefaultSize = image.Pt(480, 800)
	box         = packr.NewBox(path.Join(os.Getenv("HOME"), "DLBot"))
)

type Predefined struct {
	Locations     []Location     `xml:"Locations>Location"`
	AssetMap      []AssetMap     `xml:"AssetMap>Asset"`
	UILocations   []UILocation   `xml:"UILocations>UILocation"`
	AreaLocations []AreaLocation `xml:"AreaLocations>AreaLocation"`
	BotConst      BotConst
	rbt           *redblacktree.Tree
}

func (p *Predefined) GetAsset(key string) AssetMap {
	if val, ok := p.rbt.Get(key); ok {
		if asset, ok := val.(AssetMap); ok {
			return asset
		}
	}
	return AssetMap{}
}

func (p *Predefined) GetUILocation(key string) UILocation {
	if val, ok := p.rbt.Get(key); ok {
		if uiLocation, ok := val.(UILocation); ok {
			return uiLocation
		}
	}
	return UILocation{}
}

func (p *Predefined) GetLocation(key string) Location {
	if val, ok := p.rbt.Get(key); ok {
		if location, ok := val.(Location); ok {
			return location
		}
	}
	return Location{}
}

func (p *Predefined) GetAreaLocation(key string) AreaLocation {
	if val, ok := p.rbt.Get(key); ok {
		if areaLocation, ok := val.(AreaLocation); ok {
			return areaLocation
		}
	}
	return AreaLocation{}
}

type Boundaries struct {
	Lower image.Point
	Upper image.Point
}
type basePredefined struct {
	Key          string `xml:"key,attr"`
	PropertyName string
	Description  string
	Height       string `xml:"height,attr"`
	Width        string `xml:"width,attr"`
}

type UILocation struct {
	basePredefined
	Point image.Point
}

type AreaLocation struct {
	basePredefined
	Bounds Boundaries
}

type AssetMap struct {
	basePredefined
	Name string

	// The following fields are options but all need to be defined if using as a comparator
	Comparator  bool    `xml:"comparator,attr"`
	ScaleFactor float64 `xml:"scalefactor"`
	XThres      int     `xml:"x-threshold,attr"`
	YThres      int     `xml:"y-threshold,attr"`

	// If XThres and YThres will be phased out eventually, leave upper blank if only lower boundaries are required
	Bounds []Boundaries `xml:"Bounds>Boundary"`
}

type BotConst struct {
	StartScreenSimilarity float64
	CompareDefinitions    CompareDefinitions
	CirclesDefinitions    CirclesDefinitions
}

type CompareDefinitions struct {
	DefaultScaleFactor float64
	TrainIterations    int
}

type CirclesDefinitions struct {
	LowerBound              float64
	UpperBound              float64
	HoughCirclesDefinitions HoughCirclesDefinitions
}

type HoughCirclesDefinitions struct {
	DP        float64
	MinDist   float64
	Param1    float64
	Param2    float64
	MinRadius int
	MaxRadius int
}

type Location struct {
	basePredefined
	PageLocation int
}

func (l Location) String() string {
	return fmt.Sprintf("Location %s: page %d", l.PropertyName, l.PageLocation)
}

func GetDefaultsPredefined() *Predefined {
	v := &Predefined{}
	xmlString := box.Bytes("data.xml")
	err := xml.Unmarshal(xmlString, &v)
	if err != nil {
		log.Panic(err)
	}
	ConstructPredefined(v)
	return v
}

func ReadPredefined(r io.Reader) (*Predefined, error) {
	data, err := afero.ReadAll(r)
	if err != nil {
		return nil, err
	}
	v := &Predefined{}
	err = xml.Unmarshal(data, v)
	if err != nil {
		return nil, err
	}
	ConstructPredefined(v)
	return v, nil
}

func ConstructPredefined(v *Predefined) {
	rbt := redblacktree.NewWithStringComparator()
	var key string

	for _, value := range v.AssetMap {
		key = ConstructKey(value)
		rbt.Put(key, value)
	}

	for _, value := range v.UILocations {
		key = ConstructKey(value)
		rbt.Put(key, value)
	}

	for _, value := range v.AreaLocations {
		key = ConstructKey(value)
		rbt.Put(key, value)
	}

	v.rbt = rbt
	if v.BotConst.StartScreenSimilarity == 0 {
		v.BotConst.StartScreenSimilarity = .85
	}
}

func ConstructKey(v interface{}) (key string) {
	key = ""
	switch t := v.(type) {
	case AssetMap:
		key = AssetPrefix
		if t.Comparator {
			return key + t.Key
		}
		if t.Height == "" || t.Width == "" {
			key = key + t.Key + "-unknown"
			return
		}
		key = key + t.Key + "-" + t.Width + "x" + t.Height
		return
	case UILocation:
		key = UILocationPrefix
		if t.Height == "" || t.Width == "" {
			key = key + t.Key + "-unknown"
			return
		}
		key = key + t.Key + "-" + t.Width + "x" + t.Height
	case AreaLocation:
		key = AreaLocationPrefeix
		if t.Height == "" || t.Width == "" {
			key = key + t.Key + "-unknown"
			return
		}
		key = key + t.Key + "-" + t.Width + "x" + t.Height
	default:
		panic(fmt.Sprintf("Type: %T not valid", t))
	}
	return
}

func TransformKey(key string, dims image.Point) string {
	return fmt.Sprintf("%s-%dx%d", key, dims.X, dims.Y)
}

type Resizer interface {
	Resize(asset interface{}, to *image.Point) (interface{}, error)
}

type invalidAssetType struct {
	wrongType string
}

func (ia *invalidAssetType) Error() string {
	return fmt.Sprintf("invalid type (%s) passed to Resizer", ia.wrongType)
}

type predefinedResizer struct {
	dims image.Point
}

func (pr *predefinedResizer) Resize(asset interface{}, to *image.Point) (ret interface{}, err error) {
	var upoint image.Point
	if to == nil {
		upoint = pr.dims
	} else {
		upoint = *to
	}
	switch t := asset.(type) {
	case AssetMap:
		// TODO Imp Asset
	case AreaLocation:
		// TODO Imp AreaLocation
	case UILocation:
		resized := t
		h, _ := strconv.Atoi(t.Height)
		w, _ := strconv.Atoi(t.Width)
		Rx := float64(upoint.X) / float64(w)
		Ry := float64(upoint.Y) / float64(h)
		resized.Point.X = int(float64(resized.Point.X) * Rx)
		resized.Point.Y = int(float64(resized.Point.Y) * Ry)
		ret = resized
		return
	}
	return nil, &invalidAssetType{wrongType: fmt.Sprintf("%T", asset)}
}

func NewResizer(dims image.Point) Resizer {
	return &predefinedResizer{dims: dims}
}
