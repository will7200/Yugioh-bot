// This File Contains functions that wraps gocv
// to make the code easier to read
// these should not modify the passed variables as general rule
package base

import (
	"image"

	"gocv.io/x/gocv"
)

type IMat gocv.Mat

func NewSingleChannelScalar(val float64) gocv.Scalar {
	return gocv.NewScalar(val, val, val, val)
}

func NewMatSCScalar(val float64) gocv.Mat {
	s := NewSingleChannelScalar(val)
	return gocv.NewMatFromScalar(s, gocv.MatTypeCV64F)
}

func InRange(src, lb, ub gocv.Mat) gocv.Mat {
	mat := gocv.NewMat()
	gocv.InRange(src, lb, ub, &mat)
	return mat
}

func BitwiseAnd(src, mask gocv.Mat) gocv.Mat {
	if src.Cols() != mask.Cols() || src.Rows() != mask.Rows() || src.Channels() != mask.Channels() {
		log.Panic("src and mask do not match")
	}
	mat := gocv.NewMat()
	gocv.BitwiseAnd(src, mask, &mat)
	return mat
}

func CvtColor(src gocv.Mat, code gocv.ColorConversionCode) gocv.Mat {
	mat := gocv.NewMat()
	gocv.CvtColor(src, &mat, code)
	return mat
}

func MaskImage(src, lowerBound, upperBound gocv.Mat, applyMask bool) gocv.Mat {
	dst := gocv.NewMat()
	gocv.InRange(src, lowerBound, upperBound, &dst)
	gocv.IMWrite("dst.png", dst)
	if applyMask {
		defer dst.Close()
		ndst := gocv.NewMat()
		src.CopyToWithMask(&ndst, dst)
		return ndst
		// return BitwiseAnd(src, dst)
	}
	return dst
}

func FreeMat(mat *gocv.Mat) {
	mat.Close()
}

func ConvertTo(src *gocv.Mat, mat gocv.MatType) gocv.Mat {
	nmat := gocv.NewMat()
	src.ConvertTo(&nmat, mat)
	return nmat
}

func MatMultiply(src, src2 gocv.Mat) gocv.Mat {
	mat := gocv.NewMat()
	gocv.Multiply(src, src2, &mat)
	return mat
}
func MatDivide(src, src2 gocv.Mat) gocv.Mat {
	mat := gocv.NewMat()
	gocv.Divide(src, src2, &mat)
	return mat
}

func MatGuassianBlur(src gocv.Mat, ksize image.Point, sigmaX float64, borderType gocv.BorderType) gocv.Mat {
	mat := gocv.NewMat()
	gocv.GaussianBlur(src, &mat, ksize, sigmaX, sigmaX, borderType)
	return mat
}

func MatSubtract(src, src2 gocv.Mat) gocv.Mat {
	mat := gocv.NewMat()
	gocv.Subtract(src, src2, &mat)
	return mat
}

func MatAdd(src, src2 gocv.Mat) gocv.Mat {
	mat := gocv.NewMat()
	gocv.Add(src, src2, &mat)
	return mat
}

func PointFromKeyPoint(kp gocv.KeyPoint) image.Point {
	return image.Pt(int(kp.X), int(kp.Y))
}
