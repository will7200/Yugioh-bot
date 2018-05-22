package base

import (
	"errors"
	"math"
	"os"
	"strings"
	"sync/atomic"
	"time"

	"github.com/patrickmn/go-cache"
	plog "github.com/prometheus/common/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/afero"
	"gocv.io/x/gocv"
)

var (
	L                      = 255.0
	K1                     = 0.01
	K2                     = 0.03
	C1                     = math.Pow(K1*L, 2.0)
	C2                     = math.Pow(K2*L, 2.0)
	defWinSize             = 7
	errUnexpectedFloatType = errors.New("Non-numeric type could not be converted to float")
	errUnexpectedIntType   = errors.New("Non-numeric type could not be converted to float")
)

// Timer
type Timer struct {
	timer *time.Timer
	end   time.Time
}

// NewTimer
func NewTimer(t time.Duration) *Timer {
	return &Timer{time.NewTimer(t), time.Now().Add(t)}
}

// NewAfterFunc
func NewAfterFunc(t time.Duration, f func()) *Timer {
	return &Timer{time.AfterFunc(t, f), time.Now().Add(t)}
}

// Reset
func (s *Timer) Reset(t time.Duration) {
	s.timer.Reset(t)
	s.end = time.Now().Add(t)
}

// Stop
func (s *Timer) Stop() {
	s.timer.Stop()
}

// HasPassed
func (s *Timer) HasPassed() bool {
	return time.Now().After(s.end)
}

// GetFloat
func GetFloat(unk interface{}) (float64, error) {
	switch i := unk.(type) {
	case float64:
		return i, nil
	case float32:
		return float64(i), nil
	case int64:
		return float64(i), nil
	case int32:
		return float64(i), nil
	case int:
		return float64(i), nil
	case uint64:
		return float64(i), nil
	case uint32:
		return float64(i), nil
	case uint:
		return float64(i), nil
	default:
		return math.NaN(), errUnexpectedFloatType
	}
}

// GetInt
func GetInt(unk interface{}) (int, error) {
	switch i := unk.(type) {
	case float64:
		return int(i), nil
	case float32:
		return int(i), nil
	case int64:
		return int(i), nil
	case int32:
		return int(i), nil
	case int:
		return i, nil
	case uint64:
		return int(i), nil
	case uint32:
		return int(i), nil
	case uint:
		return int(i), nil
	default:
		return 0, errUnexpectedIntType
	}
}

// CheckWIthSourcedLog determines whether the logger will have source code line as a key
func CheckWithSourcedLog() plog.Logger {
	if !CheckIfDebug() {
		return plog.NewPassedLoggerUnsourced(logrus.StandardLogger())
	}
	return plog.NewPassedLogger(logrus.StandardLogger())
}

type debugSet struct {
	debug bool
	flag  int32
}

var ds debugSet

func (d debugSet) Set(value bool) {
	var i int32 = 0
	if value {
		i = 1
	}
	atomic.StoreInt32(&(d.flag), int32(i))
}

func (d *debugSet) Get() bool {
	if atomic.LoadInt32(&(d.flag)) != 0 {
		return true
	}
	return false
}

// CheckIfDebug checks if the instance running is debug from the args passed to the binary
func CheckIfDebug() bool {
	if ds.Get() {
		return ds.debug
	}
	ds.debug = strings.Contains(strings.Join(os.Args, " "), osArgsDebugContains)
	ds.Set(true)
	return ds.debug
}

// NewFSFromname
func NewFSFromName(name string) afero.Fs {
	name = strings.ToLower(name)
	if strings.Contains(name, "file") || strings.Contains(name, "os") {
		return afero.NewOsFs()
	}
	if strings.Contains(name, "in-memory") || strings.Contains(name, "memory") {
		return afero.NewMemMapFs()
	}
	log.Panicf("Cannot obtain file-system from %s: choose from [file,memory]", name)
	return nil
}

// NewImageCache
func NewImageCache() *cache.Cache {
	imageCache := cache.New(5*time.Minute, 10*time.Minute)
	imageCache.OnEvicted(func(s string, i interface{}) {
		switch i.(type) {
		case gocv.Mat:
			mat := i.(gocv.Mat)
			mat.Close()
		case *gocv.Mat:
			mat := i.(*gocv.Mat)
			mat.Close()
		default:

		}
	})
	return imageCache
}

// GetDefault
func GetDefault(a map[string]interface{}, val string, def interface{}) interface{} {
	if val, ok := a[val]; ok {
		return val
	}
	return def
}
