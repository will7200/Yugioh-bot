package dl

import (
	"image"
	"io"
	"reflect"
	"testing"

	"github.com/emirpasic/gods/trees/redblacktree"
)

func TestLocation_String(t *testing.T) {
	type fields struct {
		basePredefined basePredefined
		PageLocation   int
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := Location{
				basePredefined: tt.fields.basePredefined,
				PageLocation:   tt.fields.PageLocation,
			}
			if got := l.String(); got != tt.want {
				t.Errorf("Location.String() = %v, want %v", got, tt.want)
			}
		})
	}
}

/*
func Test_XMLParser(t *testing.T) {
	v := &Predefined{}
	xmlTest := box.Bytes("data.xml")

	err := xml.Unmarshal(xmlTest, &v)
	assert.Nil(t, err)
	fmt.Printf("%#v\n", v)
	_ = &Predefined{
		Locations: []Location{{PageLocation: 4, basePredefined: basePredefined{Key: "taken"}}},
	}
	tv := &BotConst{}
	tv.CirclesDefinitions = CirclesDefinitions{
		215, 255, HoughCirclesDefinitions{
			1, 45, 50, 30, 3, 60,
		},
	}
	enc := xml.NewEncoder(os.Stdout)
	enc.Indent("  ", "    ")
	if err := enc.Encode(tv); err != nil {
		fmt.Printf("error: %v\n", err)
	}
	g := GetDefaultsPredefined()
	b, err := g.rbt.ToJSON()
	if err != nil {
		assert.Nil(t, err)
	}
	ioutil.WriteFile("data.json", b, 0644)
}
*/
func TestPredefined_GetAsset(t *testing.T) {
	type fields struct {
		Locations     []Location
		AssetMap      []AssetMap
		UILocations   []UILocation
		AreaLocations []AreaLocation
		BotConst      BotConst
		rbt           *redblacktree.Tree
	}
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   AssetMap
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &Predefined{
				Locations:     tt.fields.Locations,
				AssetMap:      tt.fields.AssetMap,
				UILocations:   tt.fields.UILocations,
				AreaLocations: tt.fields.AreaLocations,
				BotConst:      tt.fields.BotConst,
				rbt:           tt.fields.rbt,
			}
			if got := p.GetAsset(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Predefined.GetAsset() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestPredefined_GetUILocation(t *testing.T) {
	type fields struct {
		Locations     []Location
		AssetMap      []AssetMap
		UILocations   []UILocation
		AreaLocations []AreaLocation
		BotConst      BotConst
		rbt           *redblacktree.Tree
	}
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   UILocation
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &Predefined{
				Locations:     tt.fields.Locations,
				AssetMap:      tt.fields.AssetMap,
				UILocations:   tt.fields.UILocations,
				AreaLocations: tt.fields.AreaLocations,
				BotConst:      tt.fields.BotConst,
				rbt:           tt.fields.rbt,
			}
			if got := p.GetUILocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Predefined.GetUILocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestPredefined_GetLocation(t *testing.T) {
	type fields struct {
		Locations     []Location
		AssetMap      []AssetMap
		UILocations   []UILocation
		AreaLocations []AreaLocation
		BotConst      BotConst
		rbt           *redblacktree.Tree
	}
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   Location
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &Predefined{
				Locations:     tt.fields.Locations,
				AssetMap:      tt.fields.AssetMap,
				UILocations:   tt.fields.UILocations,
				AreaLocations: tt.fields.AreaLocations,
				BotConst:      tt.fields.BotConst,
				rbt:           tt.fields.rbt,
			}
			if got := p.GetLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Predefined.GetLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestPredefined_GetAreaLocation(t *testing.T) {
	type fields struct {
		Locations     []Location
		AssetMap      []AssetMap
		UILocations   []UILocation
		AreaLocations []AreaLocation
		BotConst      BotConst
		rbt           *redblacktree.Tree
	}
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   AreaLocation
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &Predefined{
				Locations:     tt.fields.Locations,
				AssetMap:      tt.fields.AssetMap,
				UILocations:   tt.fields.UILocations,
				AreaLocations: tt.fields.AreaLocations,
				BotConst:      tt.fields.BotConst,
				rbt:           tt.fields.rbt,
			}
			if got := p.GetAreaLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Predefined.GetAreaLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetDefaultsPredefined(t *testing.T) {
	tests := []struct {
		name string
		want *Predefined
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := GetDefaultsPredefined(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetDefaultsPredefined() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestReadPredefined(t *testing.T) {
	type args struct {
		r io.Reader
	}
	tests := []struct {
		name    string
		args    args
		want    *Predefined
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ReadPredefined(tt.args.r)
			if (err != nil) != tt.wantErr {
				t.Errorf("ReadPredefined() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ReadPredefined() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestConstructPredefined(t *testing.T) {
	type args struct {
		v *Predefined
	}
	tests := []struct {
		name string
		args args
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ConstructPredefined(tt.args.v)
		})
	}
}

func TestConstructKey(t *testing.T) {
	type args struct {
		v interface{}
	}
	tests := []struct {
		name    string
		args    args
		wantKey string
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if gotKey := ConstructKey(tt.args.v); gotKey != tt.wantKey {
				t.Errorf("ConstructKey() = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}

func TestTransformKey(t *testing.T) {
	type args struct {
		key  string
		dims image.Point
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := TransformKey(tt.args.key, tt.args.dims); got != tt.want {
				t.Errorf("TransformKey() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_invalidAssetType_Error(t *testing.T) {
	type fields struct {
		wrongType string
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ia := &invalidAssetType{
				wrongType: tt.fields.wrongType,
			}
			if got := ia.Error(); got != tt.want {
				t.Errorf("invalidAssetType.Error() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_predefinedResizer_Resize(t *testing.T) {
	type fields struct {
		dims image.Point
	}
	type args struct {
		asset interface{}
		to    *image.Point
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		wantRet interface{}
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pr := &predefinedResizer{
				dims: tt.fields.dims,
			}
			gotRet, err := pr.Resize(tt.args.asset, tt.args.to)
			if (err != nil) != tt.wantErr {
				t.Errorf("predefinedResizer.Resize() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(gotRet, tt.wantRet) {
				t.Errorf("predefinedResizer.Resize() = %v, want %v", gotRet, tt.wantRet)
			}
		})
	}
}

func TestNewResizer(t *testing.T) {
	type args struct {
		dims image.Point
	}
	tests := []struct {
		name string
		args args
		want Resizer
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewResizer(tt.args.dims); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewResizer() = %v, want %v", got, tt.want)
			}
		})
	}
}
