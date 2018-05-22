package base

import (
	"image"
	"reflect"
	"testing"

	"runtime"

	"path"

	"github.com/mitchellh/go-homedir"
	"gocv.io/x/gocv"
)

var (
	home, _ = homedir.Dir()
	ep      = path.Join(home, "Projects", "Yugioh-bot", "assets", "start_screen.png")
)

func TestNewSingleChannelScalar(t *testing.T) {
	type args struct {
		val float64
	}
	tests := []struct {
		name string
		args args
		want gocv.Scalar
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewSingleChannelScalar(tt.args.val); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewSingleChannelScalar() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestNewMatSCScalar(t *testing.T) {
	type args struct {
		val float64
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewMatSCScalar(tt.args.val); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewMatSCScalar() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestInRange(t *testing.T) {
	type args struct {
		src gocv.Mat
		lb  gocv.Mat
		ub  gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := InRange(tt.args.src, tt.args.lb, tt.args.ub); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("InRange() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBitwiseAnd(t *testing.T) {
	type args struct {
		src  *gocv.Mat
		mask *gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := BitwiseAnd(tt.args.src, tt.args.mask); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BitwiseAnd() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestCvtColor(t *testing.T) {
	type args struct {
		src  *gocv.Mat
		code gocv.ColorConversionCode
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := CvtColor(tt.args.src, tt.args.code); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("CvtColor() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMaskImage(t *testing.T) {
	type args struct {
		src        *gocv.Mat
		lowerBound *gocv.Mat
		upperBound *gocv.Mat
		applyMask  bool
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MaskImage(tt.args.src, tt.args.lowerBound, tt.args.upperBound, tt.args.applyMask); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MaskImage() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestConvertTo(t *testing.T) {
	type args struct {
		src *gocv.Mat
		mat gocv.MatType
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := ConvertTo(tt.args.src, tt.args.mat); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ConvertTo() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMatMultiply(t *testing.T) {
	type args struct {
		src  gocv.Mat
		src2 gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MatMultiply(tt.args.src, tt.args.src2); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatMultiply() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMatDivide(t *testing.T) {
	type args struct {
		src  gocv.Mat
		src2 gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MatDivide(tt.args.src, tt.args.src2); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatDivide() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMatGuassianBlur(t *testing.T) {
	type args struct {
		src        *gocv.Mat
		ksize      image.Point
		sigmaX     float64
		borderType gocv.BorderType
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MatGuassianBlur(tt.args.src, tt.args.ksize, tt.args.sigmaX, tt.args.borderType); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatGuassianBlur() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMatSubtract(t *testing.T) {
	type args struct {
		src  *gocv.Mat
		src2 *gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MatSubtract(tt.args.src, tt.args.src2); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatSubtract() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMatAdd(t *testing.T) {
	type args struct {
		src  *gocv.Mat
		src2 *gocv.Mat
	}
	tests := []struct {
		name string
		args args
		want gocv.Mat
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MatAdd(tt.args.src, tt.args.src2); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatAdd() = %v, want %v", got, tt.want)
			}
		})
	}
}
func FakeDeferMatClose() {
	dst := gocv.NewMat()
	defer dst.Close()
	src := gocv.IMRead(ep, gocv.IMReadColor)
	defer src.Close()
	scalar := NewMatSCScalar(2.0)
	defer scalar.Close()
	gocv.Pow(src, 2, &dst)
}

func FakeMatClose() {
	dst := gocv.NewMat()
	src := gocv.IMRead(ep, gocv.IMReadColor)
	scalar := NewMatSCScalar(2.0)
	gocv.Pow(src, 2, &dst)
	dst.Close()
	scalar.Close()
	src.Close()
}

func FakeMatRunTime() {
	dst := gocv.NewMat()
	runtime.SetFinalizer(&dst, freeMat)
	src := gocv.IMRead(ep, gocv.IMReadColor)
	runtime.SetFinalizer(&src, freeMat)
	scalar := NewMatSCScalar(2.0)
	runtime.SetFinalizer(&scalar, freeMat)
	gocv.Pow(src, 2, &dst)
}

func BenchmarkFakeDeferMatClose(b *testing.B) {
	for i := 0; i < b.N; i++ {
		FakeDeferMatClose()
	}
}

func BenchmarkFakeMatClose(b *testing.B) {
	for i := 0; i < b.N; i++ {
		FakeMatClose()
	}
}

func BenchmarkFakeMatRunTime(b *testing.B) {
	for i := 0; i < b.N; i++ {
		FakeMatRunTime()
	}
}
