package dl

import (
	"encoding/xml"
	"fmt"
	"image"
	"io"
	"strconv"

	"github.com/emirpasic/gods/trees/redblacktree"
	"github.com/spf13/afero"
)

var (
	DefaultSize = image.Pt(480, 800)
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

type basePredefined struct {
	Key          string `xml:"key,attr"`
	PropertyName string
	Description  string
}

type UILocation struct {
	basePredefined
	Point  image.Point
	Height string `xml:"height,attr"`
	Width  string `xml:"width,attr"`
}

type AreaLocation struct {
	basePredefined
	Left, Top, Width, Height int
}

type AssetMap struct {
	basePredefined
	Name   string
	Height string `xml:"height,attr"`
	Width  string `xml:"width,attr"`

	// The following fields are options but all need to be defined if using as a comparator
	Comparator  bool    `xml:"comparator,attr"`
	ScaleFactor float64 `xml:"scalefactor"`
	XThres      int     `xml:"x-threshold,attr"`
	YThres      int     `xml:"y-threshold,attr"`
}

type BotConst struct {
	StartScreenSimilarity float64
}

type Location struct {
	basePredefined
	PageLocation int
}

func (l Location) String() string {
	return fmt.Sprintf("Location %s: page %d", l.PropertyName, l.PageLocation)
}

var xmlString = `
<?xml version="1.0" encoding="UTF-8" ?>
<Predefined>
	<Locations>
		<Location key="quick_rank_duel">
			<PropertyName>Quick RankDuels</PropertyName>
			<Description></Description>
			<PageLocation>2</PageLocation>
		</Location>
		<Location key="street_replay">
			<PropertyName>Street Replay</PropertyName>
			<Description></Description>
			<PageLocation>4</PageLocation>
		</Location>
	</Locations>
	<AssetMap>
		<Asset key="start_screen" height="800" width="480">
			<Name>new_open.png</Name>
		</Asset>
	</AssetMap>
	<UILocations>
		<UILocation key="initiate_link" height="800" width="480">
			<PropertyName>Yugioh Initiate Link</PropertyName>
			<Description>Location of ui button to pass through start screen</Description>
			<Point>
				<X>240</X>
				<Y>530</Y>
			</Point>
		</UILocation>
	</UILocations>
</Predefined>`

func GetDefaultsPredefined() *Predefined {
	v := &Predefined{}
	err := xml.Unmarshal([]byte(xmlString), &v)
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
	v.rbt = rbt
	if v.BotConst.StartScreenSimilarity == 0 {
		v.BotConst.StartScreenSimilarity = .85
	}
}

func ConstructKey(v interface{}) (key string) {
	key = ""
	switch t := v.(type) {
	case AssetMap:
		key = "Asset-"
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
		key = "UILocation-"
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
