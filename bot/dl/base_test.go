package dl

import (
	"context"
	"image"
	"reflect"
	"testing"

	"github.com/otiai10/gosseract"
	"github.com/patrickmn/go-cache"
	"github.com/spf13/afero"
	"gocv.io/x/gocv"
)

func TestCheckIfBattle(t *testing.T) {
	type args struct {
		img        gocv.Mat
		percentage float64
		options    Options
	}
	tests := []struct {
		name    string
		args    args
		want    bool
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := CheckIfBattle(tt.args.img, tt.args.percentage, tt.args.options)
			if (err != nil) != tt.wantErr {
				t.Errorf("CheckIfBattle() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("CheckIfBattle() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestOpenUIAsset(t *testing.T) {
	type args struct {
		name  string
		home  string
		appfs afero.Fs
	}
	tests := []struct {
		name    string
		args    args
		want    afero.File
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := OpenUIAsset(tt.args.name, tt.args.home, tt.args.appfs)
			if (err != nil) != tt.wantErr {
				t.Errorf("OpenUIAsset() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("OpenUIAsset() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetUIPath(t *testing.T) {
	type args struct {
		name string
		home string
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
			if got := GetUIPath(tt.args.name, tt.args.home); got != tt.want {
				t.Errorf("GetUIPath() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetImageFromAsset(t *testing.T) {
	type args struct {
		asset   AssetMap
		options Options
	}
	tests := []struct {
		name    string
		args    args
		want    gocv.Mat
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetImageFromAsset(tt.args.asset, tt.args.options)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetImageFromAsset() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetImageFromAsset() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestTryImageFromCache(t *testing.T) {
	type args struct {
		asset   AssetMap
		options Options
		c       *cache.Cache
	}
	tests := []struct {
		name    string
		args    args
		want    gocv.Mat
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := TryImageFromCache(tt.args.asset, tt.args.options, tt.args.c)
			if (err != nil) != tt.wantErr {
				t.Errorf("TryImageFromCache() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("TryImageFromCache() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestRegisterProvider(t *testing.T) {
	type args struct {
		name  string
		value NewProvider
	}
	tests := []struct {
		name string
		args args
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			RegisterProvider(tt.args.name, tt.args.value)
		})
	}
}

func TestGetProvider(t *testing.T) {
	type args struct {
		name    string
		options *Options
	}
	tests := []struct {
		name string
		args args
		want Provider
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := GetProvider(tt.args.name, tt.args.options); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetProvider() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestPreCheckError_Error(t *testing.T) {
	type fields struct {
		Reason error
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
			e := &PreCheckError{
				Reason: tt.fields.Reason,
			}
			if got := e.Error(); got != tt.want {
				t.Errorf("PreCheckError.Error() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGenericWaitFor(t *testing.T) {
	type args struct {
		ctx            context.Context
		provider       Provider
		messeage       string
		checkCondition func(interface{}) bool
		fn             func(map[string]interface{}) interface{}
		args           map[string]interface{}
	}
	tests := []struct {
		name    string
		args    args
		want    bool
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GenericWaitFor(tt.args.ctx, tt.args.provider, tt.args.messeage, tt.args.checkCondition, tt.args.fn, tt.args.args)
			if (err != nil) != tt.wantErr {
				t.Errorf("GenericWaitFor() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GenericWaitFor() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetImage(t *testing.T) {
	type args struct {
		key     string
		matType gocv.IMReadFlag
		options Options
	}
	tests := []struct {
		name    string
		args    args
		want    *gocv.Mat
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetImage(tt.args.key, tt.args.matType, tt.args.options)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetImage() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetImage() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestIsStartScreen(t *testing.T) {
	type args struct {
		img     gocv.Mat
		options Options
	}
	tests := []struct {
		name    string
		args    args
		want    bool
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := IsStartScreen(tt.args.img, tt.args.options)
			if (err != nil) != tt.wantErr {
				t.Errorf("IsStartScreen() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("IsStartScreen() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestImgToString(t *testing.T) {
	img := gocv.IMRead("/Users/williamflores/DLBot/assets/ok_box.png", gocv.IMReadGrayScale)
	cropped := img.Region(image.Rect(20, 15, img.Cols()-19, img.Rows()-15))
	img.Close()
	cimg := gocv.IMRead("/Users/williamflores/DLBot/assets/close.png", gocv.IMReadGrayScale)
	cropped2 := cimg.Region(image.Rect(20, 15, cimg.Cols()-19, cimg.Rows()-15))
	cimg.Close()
	defer cropped.Close()
	type args struct {
		img     gocv.Mat
		charSet string
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{"Ok",
			args{cropped, "OK"},
			"OK",
			false,
		},
		{"Closed",
			args{cropped2, "CLOSE"},
			"CLOSE",
			false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ImgToString(tt.args.img, tt.args.charSet)
			if (err != nil) != tt.wantErr {
				t.Errorf("ImgToString() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("ImgToString() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkImgToString(b *testing.B) {
	b.StopTimer()
	img := gocv.IMRead("/Users/williamflores/DLBot/assets/ok_box.png", gocv.IMReadGrayScale)
	cropped := img.Region(image.Rect(20, 15, img.Cols()-19, img.Rows()-15))
	img.Close()
	b.StartTimer()
	for i := 0; i < b.N; i++ {
		ImgToString(cropped, "OK")
	}
}

func TestClientImgToString(t *testing.T) {
	type args struct {
		client gosseract.Client
		img    gocv.Mat
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ClientImgToString(tt.args.client, tt.args.img)
			if (err != nil) != tt.wantErr {
				t.Errorf("ClientImgToString() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("ClientImgToString() = %v, want %v", got, tt.want)
			}
		})
	}
}
