package base

import (
	"time"
	"os"
	"strings"

	"github.com/spf13/afero"
	"github.com/sirupsen/logrus"
	plog "github.com/prometheus/common/log"
	"sync/atomic"
)

func CreateModuleLog(module ...string) *logrus.Entry {
	if len(module) > 0 {
		return logrus.WithField("module", module[0])
	}
	return logrus.WithField("module", nil)
}

func CreateCustomModuleLog(logger *logrus.Logger, module ...string) *logrus.Entry {
	if len(module) > 0 {
		return logger.WithField("module", module[0])
	}
	return logrus.WithField("module", nil)
}

type Timer struct {
	timer *time.Timer
	end   time.Time
}

func NewTimer(t time.Duration) *Timer {
	return &Timer{time.NewTimer(t), time.Now().Add(t)}
}

func NewAfterFunc(t time.Duration, f func()) *Timer {
	return &Timer{time.AfterFunc(t, f), time.Now().Add(t)}
}

func (s *Timer) Reset(t time.Duration) {
	s.timer.Reset(t)
	s.end = time.Now().Add(t)
}

func (s *Timer) Stop() {
	s.timer.Stop()
}

func (s *Timer) HasPassed() bool {
	return time.Now().After(s.end)
}

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

func CheckIfDebug() bool {
	if ds.Get() {
		return ds.debug
	}
	ds.debug = strings.Contains(strings.Join(os.Args, " "), "debug")
	ds.Set(true)
	return ds.debug
}

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
