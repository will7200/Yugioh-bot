package base

import (
	"errors"
	"image"
	"image/color"
	"math"

	"gocv.io/x/gocv"
)

func SSIM_Image(x, y image.Image) float64 {
	avg_x := mean(x)
	avg_y := mean(y)

	stdev_x := stdev(x)
	stdev_y := stdev(y)

	cov, err := covar(x, y)
	if err != nil {
		log.Panic(err)
	}
	numerator := ((2.0 * avg_x * avg_y) + C1) * ((2.0 * cov) + C2)
	denominator := (math.Pow(avg_x, 2.0) + math.Pow(avg_y, 2.0) + C1) *
		(math.Pow(stdev_x, 2.0) + math.Pow(stdev_y, 2.0) + C2)

	return numerator / denominator
}

func SSIM_GOCV(x, y gocv.Mat) float64 {

	defPoint := image.Pt(defWinSize, defWinSize)
	defSigma := 1.5
	I1, I2 := ConvertTo(&x, gocv.MatTypeCV64F), ConvertTo(&y, gocv.MatTypeCV64F)
	I2_2 := MatMultiply(I2, I2)
	I1_2 := MatMultiply(I1, I1)
	I1_I2 := MatMultiply(I1, I2)

	mu1 := MatGuassianBlur(I1, defPoint, defSigma, gocv.BorderReflect)
	I1.Close()

	mu2 := MatGuassianBlur(I2, defPoint, defSigma, gocv.BorderReflect)
	I2.Close()

	mu1_2 := MatMultiply(mu1, mu1)
	mu2_2 := MatMultiply(mu2, mu2)
	mu1_mu2 := MatMultiply(mu1, mu2)

	mu1.Close()
	mu2.Close()

	sigmal1_2t := MatGuassianBlur(I1_2, defPoint, defSigma, gocv.BorderReflect)
	I1_2.Close()
	sigmal1_2 := MatSubtract(sigmal1_2t, mu1_2)

	sigmal2_2t := MatGuassianBlur(I2_2, defPoint, defSigma, gocv.BorderReflect)
	I2_2.Close()
	sigmal2_2 := MatSubtract(sigmal2_2t, mu2_2)

	sigmal2t := MatGuassianBlur(I1_I2, defPoint, defSigma, gocv.BorderReflect)
	I1_I2.Close()
	sigmal2 := MatSubtract(sigmal2t, mu1_mu2)

	sigmal1_2t.Close()

	sigmal2_2t.Close()

	sigmal2t.Close()

	scalar2 := NewMatSCScalar(2.0)
	scalarC1 := NewMatSCScalar(C1)
	scalarC2 := NewMatSCScalar(C2)

	t1t := MatMultiply(mu1_mu2, scalar2)
	mu1_mu2.Close()

	t1 := MatAdd(t1t, scalarC1)
	t2t := MatMultiply(sigmal2, scalar2)
	sigmal2.Close()
	t2 := MatAdd(t2t, scalarC2)
	t3 := MatMultiply(t1, t2)

	t1t.Close()
	t1.Close()
	t2t.Close()
	t2.Close()
	defer t3.Close()

	t1tm := MatAdd(mu1_2, mu2_2)
	mu1_2.Close()
	mu2_2.Close()
	t1m := MatAdd(t1tm, scalarC1)
	t1tm.Close()

	t2tm := MatAdd(sigmal1_2, sigmal2_2)
	sigmal1_2.Close()
	sigmal2_2.Close()
	t2m := MatAdd(t2tm, scalarC2)
	t2tm.Close()

	scalarC1.Close()
	scalarC2.Close()
	scalar2.Close()

	t1mm := MatMultiply(t1m, t2m)

	t1m.Close()
	t2m.Close()
	defer t1mm.Close()

	ssimMap := MatDivide(t3, t1mm)
	val := ssimMap.Mean().Val1
	ssimMap.Close()
	return val
}

// Convert uint32 R value to a float. The returnng
// float will have a range of 0-255
func getPixVal(c color.Color) float64 {
	r, _, _, _ := c.RGBA()
	return float64(r >> 8)
}

// Helper function that return the dimension of an image
func dim(img image.Image) (w, h int) {
	w, h = img.Bounds().Max.X, img.Bounds().Max.Y
	return
}

// Check if two images have the same dimension
func equalDim(img1, img2 image.Image) bool {
	w1, h1 := dim(img1)
	w2, h2 := dim(img2)
	return (w1 == w2) && (h1 == h2)
}

func CVEqualDim(img1, img2 gocv.Mat) bool {
	return (img1.Rows() == img2.Rows()) && (img1.Cols() == img2.Cols())
}

// Given an Image, calculate the mean of its
// pixel values
func mean(img image.Image) float64 {
	w, h := dim(img)
	n := float64((w * h) - 1)
	sum := 0.0

	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			sum += getPixVal(img.At(x, y))
		}
	}
	return sum / n
}

// Compute the standard deviation with pixel values of Image
func stdev(img image.Image) float64 {
	w, h := dim(img)

	n := float64((w * h) - 1)
	sum := 0.0
	avg := mean(img)

	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			pix := getPixVal(img.At(x, y))
			sum += math.Pow((pix - avg), 2.0)
		}
	}
	return math.Sqrt(sum / n)
}

// Calculate the covariance of 2 images
func covar(img1, img2 image.Image) (c float64, err error) {
	if !equalDim(img1, img2) {
		err = errors.New("Images must have same dimension")
		return
	}
	avg1 := mean(img1)
	avg2 := mean(img2)
	w, h := dim(img1)
	sum := 0.0
	n := float64((w * h) - 1)

	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {
			pix1 := getPixVal(img1.At(x, y))
			pix2 := getPixVal(img2.At(x, y))
			sum += (pix1 - avg1) * (pix2 - avg2)
		}
	}
	c = sum / n
	return
}
