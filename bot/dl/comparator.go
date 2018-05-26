package dl

import (
	"fmt"

	cluster2 "github.com/cdipaolo/goml/cluster"
	"github.com/patrickmn/go-cache"
	"github.com/will7200/Yugioh-bot/bot/base"
	"gocv.io/x/gocv"
	"gocv.io/x/gocv/contrib"
)

// Correlation
type Correlation int

// comparator
type comparator struct {
	predefined *Predefined
	cache      *cache.Cache
	options    *Options
}

// Compare
func (c *comparator) Compare(key string, img gocv.Mat, correlation Correlation) bool {
	asset := c.predefined.GetAsset(AssetPrefix + key)
	if asset == (AssetMap{}) {
		log.Panic(fmt.Sprintf("Comparator %s does not exist", key))
	}
	trainImage, err := TryImageFromCache(asset, *c.options, c.cache)
	if err != nil {
		log.Panic(err)
	}
	if trainImage.Empty() || img.Empty() {
		log.Panic("image is empty")
	}
	var scaleFactor float64
	scaleFactor = asset.ScaleFactor
	if asset.ScaleFactor == 0 {
		scaleFactor = .80
	}
	sift := contrib.NewSIFT()
	defer sift.Close()
	mask := gocv.NewMat()

	kp1, des1 := sift.DetectAndCompute(trainImage, mask)
	kp2, des2 := sift.DetectAndCompute(img, mask)

	defer des1.Close()
	defer des2.Close()

	if des1.Empty() || des2.Empty() {
		return false
	}
	bf := gocv.NewBFMatcher()
	defer bf.Close()
	matches := bf.KnnMatch(des1, des2, 2)
	goodMatches := make([]gocv.DMatch, 0, len(matches))
	cluster := make([][]float64, 0, len(matches))
	for i := range matches {
		m, n := matches[i][0], matches[i][1]
		kpQuery := kp1[m.QueryIdx]
		kpTrain := kp2[m.TrainIdx]
		_, p2 := base.PointFromKeyPoint(kpQuery), base.PointFromKeyPoint(kpTrain)
		if m.Distance < scaleFactor*n.Distance && p2.Y > asset.YThres && p2.X < asset.XThres {
			goodMatches = append(goodMatches, m)
			cluster = append(cluster, []float64{kpTrain.X, kpTrain.Y})
		}
	}
	log.Debugf("SIFT run for %s correlation %d: %d, %t", asset.Description, correlation, len(cluster), len(cluster) > int(correlation))
	if len(cluster) < int(correlation) {
		return false
	}

	log.Debug("Running clustering algo")
	model := cluster2.NewKMeans(1, 300, cluster)

	if model.Learn() != nil {
		log.Panic("Could not train model")
	}
	// log.Info(model.Centroids[0])
	// matches =
	return false
}

// Comparator
type Comparator interface {
	Compare(key string, img gocv.Mat, correlation Correlation) bool
}

// NewComparator
func NewComparator(options *Options) Comparator {
	return &comparator{
		options.Predefined,
		options.ImageCache,
		options,
	}
}

// NewComparatorWithCache
func NewComparatorWithCache(options *Options, c *cache.Cache) Comparator {
	return &comparator{
		predefined: options.Predefined,
		cache:      c,
		options:    options,
	}
}
