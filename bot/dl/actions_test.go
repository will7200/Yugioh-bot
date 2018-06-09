package dl

import (
	"reflect"
	"testing"
	"time"

	"github.com/mitchellh/go-homedir"
	"github.com/stretchr/testify/assert"
	"github.com/will7200/Yugioh-bot/bot/base"
	"gocv.io/x/gocv"
)

func FakeActions(t *testing.T) *BaseActions {
	home, err := homedir.Expand(base.HomeDir)
	assert.Nil(t, err)
	d := &base.Dispatcher{}
	options := &Options{
		Dispatcher: d,
		IsRemote:   false,
		Path:       "",
		FileSystem: base.NewFSFromName("in-memory"),
		HomeDir:    home,
		Predefined: GetDefaultsPredefined(),
		ImageCache: base.NewImageCache(),
	}
	actions := NewActions(options)
	return actions.(*BaseActions)
}
func TestBaseActions_TakePNGScreenShot(t *testing.T) {
	tests := []struct {
		name      string
		action    *BaseActions
		want      []byte
		wantErr   bool
		wantPanic bool
	}{
		{
			"Generic",
			FakeActions(t),
			[]byte{},
			false,
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseActions.TakePNGScreenShot() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			got, err := tt.action.TakePNGScreenShot()
			if (err != nil) != tt.wantErr {
				t.Errorf("BaseActions.TakePNGScreenShot() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseActions.TakePNGScreenShot() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseActions_Tap(t *testing.T) {
	type args struct {
		args []interface{}
	}
	tests := []struct {
		name      string
		action    *BaseActions
		args      args
		wantPanic bool
	}{
		{
			"Generic",
			FakeActions(t),
			args{args: []interface{}{}},
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseActions.Tap() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.action.Tap(tt.args.args...)
		})
	}
}

func TestBaseActions_Swipe(t *testing.T) {
	type args struct {
		args []interface{}
	}
	tests := []struct {
		name      string
		action    *BaseActions
		args      args
		wantPanic bool
	}{
		{
			"Generic",
			FakeActions(t),
			args{args: []interface{}{}},
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseActions.Swipe() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.action.Swipe(tt.args.args...)
		})
	}
}

func TestBaseActions_SwipeTime(t *testing.T) {
	type args struct {
		args []interface{}
	}
	tests := []struct {
		name      string
		action    *BaseActions
		args      args
		wantPanic bool
	}{
		{
			"Generic",
			FakeActions(t),
			args{args: []interface{}{}},
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseActions.SwipeActions() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.action.SwipeTime(tt.args.args...)
		})
	}
}

func TestBaseActions_WaitForUi(t *testing.T) {
	type args struct {
		timeSleep time.Duration
	}
	tests := []struct {
		name   string
		action *BaseActions
		args   args
	}{
		{
			"Generic",
			FakeActions(t),
			args{1 * time.Millisecond},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.action.WaitForUi(tt.args.timeSleep)
		})
	}
}

func TestBaseActions_GetImgFromScreenShot(t *testing.T) {
	type args struct {
		fromCache bool
		fail      int
	}
	tests := []struct {
		name      string
		action    *BaseActions
		args      args
		want      gocv.Mat
		wantPanic bool
	}{
		{
			"Generic",
			FakeActions(t),
			args{fromCache: false, fail: 5},
			gocv.NewMat(),
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseActions.GetImgFromScreenShot() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			if got := tt.action.GetImgFromScreenShot(tt.args.fromCache, tt.args.fail); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("BaseActions.GetImgFromScreenShot() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestNewActions(t *testing.T) {
	type args struct {
		o *Options
	}
	tests := []struct {
		name string
		args args
		want Actions
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewActions(tt.args.o); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewActions() = %v, want %v", got, tt.want)
			}
		})
	}
}
