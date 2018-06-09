package dl

import (
	"encoding/xml"
	"reflect"
	"testing"

	"github.com/patrickmn/go-cache"
	"github.com/stretchr/testify/assert"
	"github.com/will7200/Yugioh-bot/bot/base"
	"gocv.io/x/gocv"
)

func Test_detector_Compare(t *testing.T) {
	type fields struct {
		predefined *Predefined
		cache      *cache.Cache
		options    *Options
	}
	type args struct {
		key         string
		img         gocv.Mat
		correlation Correlation
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			d := &detector{
				predefined: tt.fields.predefined,
				cache:      tt.fields.cache,
				options:    tt.fields.options,
			}
			if got, _ := d.Compare(tt.args.key, tt.args.img, tt.args.correlation); got != tt.want {
				t.Errorf("detector.Compare() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_detector_Circles(t *testing.T) {
	type fields struct {
		predefined *Predefined
		cache      *cache.Cache
		options    *Options
	}
	type args struct {
		key string
		img gocv.Mat
	}
	v := &Predefined{}
	xmlTest := box.Bytes("data.xml")
	err := xml.Unmarshal([]byte(xmlTest), &v)
	assert.Nil(t, err)
	imgCache := base.NewImageCache()
	img := gocv.IMRead("/Users/williamflores/DLBot/assets/test_case_npc_detection.png", gocv.IMReadColor)
	tests := []struct {
		name   string
		fields fields
		args   args
		want   []Circle
		want1  bool
	}{
		{
			name:   "Test Circles Case 1",
			fields: fields{predefined: GetDefaultsPredefined(), cache: imgCache},
			args:   args{"npc_detection", img},
			want:   []Circle{},
			want1:  false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			d := &detector{
				predefined: tt.fields.predefined,
				cache:      tt.fields.cache,
				options:    tt.fields.options,
			}
			got, got1 := d.Circles(tt.args.key, tt.args.img)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("detector.Circles() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				t.Errorf("detector.Circles() got1 = %v, want %v", got1, tt.want1)
			}
		})
	}
}

func TestNewDetector(t *testing.T) {
	type args struct {
		options *Options
	}
	tests := []struct {
		name string
		args args
		want Detector
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewDetector(tt.args.options); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewDetector() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestNewDetectorWithCache(t *testing.T) {
	type args struct {
		options *Options
		c       *cache.Cache
	}
	tests := []struct {
		name string
		args args
		want Detector
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewDetectorWithCache(tt.args.options, tt.args.c); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewDetectorWithCache() = %v, want %v", got, tt.want)
			}
		})
	}
}
