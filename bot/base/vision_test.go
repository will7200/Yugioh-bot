package base

import (
	"testing"

	"gocv.io/x/gocv"
)

func BenchmarkSSIM_GOCV(b *testing.B) {
	b.StopTimer()
	src := gocv.IMRead(ep, gocv.IMReadColor)
	dst := gocv.IMRead(ep, gocv.IMReadColor)
	defer src.Close()
	defer dst.Close()
	b.StartTimer()
	for i := 0; i < b.N; i++ {
		SSIM_GOCV(&src, &dst)
	}
}

func BenchmarkSSIM_IMAGE(b *testing.B) {
	b.StopTimer()
	src := gocv.IMRead(ep, gocv.IMReadColor)
	dst := gocv.IMRead(ep, gocv.IMReadColor)
	defer src.Close()
	defer dst.Close()
	srcImage, _ := src.ToImage()
	dstImage, _ := dst.ToImage()
	b.StartTimer()
	for i := 0; i < b.N; i++ {
		SSIM_Image(srcImage, dstImage)
	}
}
