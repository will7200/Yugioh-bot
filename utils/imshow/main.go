package main

import (
	"gocv.io/x/gocv"
	"os"
	"image"
	"gopkg.in/alecthomas/kingpin.v2"
)

var (
	app = kingpin.New("imshow", "shows image because the other program can't")

	show       = app.Command("show", "Show img to user")
	imageName  = show.Arg("file", "image to show").Required().String()
	xdirection = show.Flag("scale-factor-x", "Scaling factor the x direction").Float64()
	ydirection = show.Flag("scale-factor-y", "Scaling factor the y direction").Float64()
	fillMethod = show.Flag("fill-method", "Fill method for shrinking and streching").Int()
)

func init() {
	//runtime.LockOSThread()
}

func main() {
	switch kingpin.MustParse(app.Parse(os.Args[1:])) {
	case show.FullCommand():
		img := gocv.IMRead(*imageName, gocv.IMReadAnyColor)
		if img.Empty() {
			panic("cannot read image")
		}
		window := gocv.NewWindow(os.Args[1])
		mat := gocv.NewMat()
		var fm gocv.InterpolationFlags
		switch *fillMethod {
		case 0:
			fm = gocv.InterpolationNearestNeighbor
		case 1:
			fm = gocv.InterpolationLinear
		case 2:
			fm = gocv.InterpolationCubic
		case 3:
			fm = gocv.InterpolationArea
		case 4:
			fm = gocv.InterpolationLanczos4
		case 7:
			fm = gocv.InterpolationMax
		default:
			fm = gocv.InterpolationDefault

		}
		if *xdirection == 0 {
			*xdirection = 1
		}
		if *ydirection == 0 {
			*ydirection = 1
		}
		gocv.Resize(img, &mat, image.Point{}, *xdirection, *ydirection, fm)
		for {
			window.IMShow(mat)
			if window.WaitKey(1) >= 0 {
				break
			}
		}
		err := window.Close()
		if err != nil {
			os.Exit(1)
		}
	}
}
