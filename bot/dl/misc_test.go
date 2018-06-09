package dl

import (
	"image"
	"reflect"
	"testing"

	"github.com/mitchellh/go-homedir"
	"github.com/stretchr/testify/assert"
	"github.com/will7200/Yugioh-bot/bot/base"
	"gocv.io/x/gocv"
)

type fakeMisc struct {
	BaseMiscellaneous
	dims image.Point
}

func (bm *fakeMisc) ScreenDimensions() image.Point {
	return bm.dims
}

func FakeMisc(t *testing.T) *BaseMiscellaneous {
	home, err := homedir.Expand(base.HomeDir)
	assert.Nil(t, err)
	d := &base.Dispatcher{}
	options := &Options{
		Dispatcher: d,
		IsRemote:   false,
		Path:       "",
		FileSystem: base.NewFSFromName("in-memory"),
		HomeDir:    home,
		Predefined: GetDefaultsPredefined(),
		ImageCache: base.NewImageCache(),
	}
	bm := BaseMiscellaneous{}
	fm := fakeMisc{bm, image.Pt(4, 10)}
	provider := BaseProvider{
		NewActions(options),
		NewDuelLinks(options),
		&fm,
	}
	options.Provider = provider
	bm.options = options
	bm.predefined = options.Predefined
	return &bm
}

func TestBaseMiscellaneous_Options(t *testing.T) {
	bm := FakeMisc(t)
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		want *Options
	}{
		{
			"Test Options Getter",
			bm,
			bm.options,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.Options(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.Options() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_ScreenDimensions(t *testing.T) {
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		want image.Point
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.ScreenDimensions(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.ScreenDimensions() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_GetAsset(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		args args
		want AssetMap
	}{
		{
			"Generic",
			FakeMisc(t),
			args{key: "fake"},
			AssetMap{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.GetAsset(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.GetAsset() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_GetUILocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		args args
		want UILocation
	}{
		{
			"Generic",
			FakeMisc(t),
			args{key: "fake"},
			UILocation{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.GetUILocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.GetUILocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_GetLocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		args args
		want Location
	}{
		{
			"Generic",
			FakeMisc(t),
			args{key: "fake"},
			Location{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.GetLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.GetLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_GetAreaLocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		bm   *BaseMiscellaneous
		args args
		want AreaLocation
	}{
		{
			"Generic",
			FakeMisc(t),
			args{key: "fake"},
			AreaLocation{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.bm.GetAreaLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseMiscellaneous.GetAreaLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_PreCheck(t *testing.T) {
	tests := []struct {
		name    string
		b       *BaseMiscellaneous
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := tt.b.PreCheck(); (err != nil) != tt.wantErr {
				t.Errorf("BaseMiscellaneous.PreCheck() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestBaseMiscellaneous_IsProcessRunning(t *testing.T) {
	tests := []struct {
		name string
		b    *BaseMiscellaneous
		want bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.b.IsProcessRunning(); got != tt.want {
				t.Errorf("BaseMiscellaneous.IsProcessRunning() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseMiscellaneous_StartProcess(t *testing.T) {
	tests := []struct {
		name string
		b    *BaseMiscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.b.StartProcess()
		})
	}
}

func TestBaseMiscellaneous_KillProcess(t *testing.T) {
	tests := []struct {
		name string
		b    *BaseMiscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.b.KillProcess()
		})
	}
}

func TestBaseMiscellaneous_EnsureResolutionMatches(t *testing.T) {
	type args struct {
		mat *gocv.Mat
	}
	tests := []struct {
		name string
		b    *BaseMiscellaneous
		args args
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.b.EnsureResolutionMatches(tt.args.mat)
		})
	}
}

func TestNewMisc(t *testing.T) {
	type args struct {
		o *Options
	}
	tests := []struct {
		name string
		args args
		want Miscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewMisc(tt.args.o); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewMisc() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_Options(t *testing.T) {
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		want *Options
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.Options(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.Options() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_IsProcessRunning(t *testing.T) {
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		want bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.IsProcessRunning(); got != tt.want {
				t.Errorf("fallBackMiscellaneous.IsProcessRunning() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_StartProcess(t *testing.T) {
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.fb.StartProcess()
		})
	}
}

func Test_fallBackMiscellaneous_KillProcess(t *testing.T) {
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.fb.KillProcess()
		})
	}
}

func Test_fallBackMiscellaneous_EnsureResolutionMatches(t *testing.T) {
	type args struct {
		mat *gocv.Mat
	}
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		args args
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.fb.EnsureResolutionMatches(tt.args.mat)
		})
	}
}

func Test_fallBackMiscellaneous_PreCheck(t *testing.T) {
	tests := []struct {
		name    string
		fb      *fallBackMiscellaneous
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := tt.fb.PreCheck(); (err != nil) != tt.wantErr {
				t.Errorf("fallBackMiscellaneous.PreCheck() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func Test_fallBackMiscellaneous_ScreenDimensions(t *testing.T) {
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		want image.Point
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.ScreenDimensions(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.ScreenDimensions() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_GetAsset(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		args args
		want AssetMap
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.GetAsset(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.GetAsset() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_GetUILocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		args args
		want UILocation
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.GetUILocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.GetUILocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_GetLocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		args args
		want Location
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.GetLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.GetLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_fallBackMiscellaneous_GetAreaLocation(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name string
		fb   *fallBackMiscellaneous
		args args
		want AreaLocation
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.fb.GetAreaLocation(tt.args.key); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fallBackMiscellaneous.GetAreaLocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestWithFallBackMiscellaneous(t *testing.T) {
	type args struct {
		misc        Miscellaneous
		predefined  *Predefined
		defaultDims image.Point
	}
	tests := []struct {
		name string
		args args
		want Miscellaneous
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := WithFallBackMiscellaneous(tt.args.misc, tt.args.predefined, tt.args.defaultDims); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("WithFallBackMiscellaneous() = %v, want %v", got, tt.want)
			}
		})
	}
}
