package dl

import (
	"reflect"
	"testing"

	"github.com/mitchellh/go-homedir"
	"github.com/stretchr/testify/assert"
	"github.com/will7200/Yugioh-bot/bot/base"
)

func FakeDuelLinks(t *testing.T) *BaseDuelLinks {
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
	duelLinks := NewDuelLinks(options)
	return duelLinks.(*BaseDuelLinks)
}

func TestBaseDuelLinks_SpecialEvents(t *testing.T) {
	type args struct {
		info DuelLinksInstanceInfo
	}
	tests := []struct {
		name      string
		b         *BaseDuelLinks
		args      args
		wantPanic bool
	}{
		{
			"Generic",
			FakeDuelLinks(t),
			args{info: DuelLinksInstanceInfo{}},
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseDuelLinks.SpecialEvents() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.b.SpecialEvents(tt.args.info)
		})
	}
}

func TestBaseDuelLinks_ScanFor(t *testing.T) {
	tests := []struct {
		name      string
		b         *BaseDuelLinks
		wantPanic bool
	}{
		{
			"Generic",
			FakeDuelLinks(t),
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseDuelLinks.ScanFor() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.b.ScanFor()
		})
	}
}

func TestBaseDuelLinks_InitialScreen(t *testing.T) {
	type args struct {
		in0 bool
	}
	tests := []struct {
		name      string
		b         *BaseDuelLinks
		args      args
		want      bool
		wantErr   bool
		wantPanic bool
	}{
		{
			"Generic",
			FakeDuelLinks(t),
			args{in0: false},
			false,
			false,
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseDuelLinks.InitialScreen() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			got, err := tt.b.InitialScreen(tt.args.in0)
			if (err != nil) != tt.wantErr {
				t.Errorf("BaseDuelLinks.InitialScreen() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("BaseDuelLinks.InitialScreen() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestBaseDuelLinks_WaitFor(t *testing.T) {
	tests := []struct {
		name      string
		b         *BaseDuelLinks
		wantPanic bool
	}{
		{
			"Generic",
			FakeDuelLinks(t),
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				r := recover()
				if (r != nil) != tt.wantPanic {
					t.Errorf("BaseDuelLinks.WaitFor() recover = %v, wantPanic = %v", r, tt.wantPanic)
				}
			}()
			tt.b.WaitFor()
		})
	}
}

func TestNewDuelLinks(t *testing.T) {
	type args struct {
		no *Options
	}
	tests := []struct {
		name      string
		args      args
		want      DuelLinks
		wantPanic bool
	}{}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewDuelLinks(tt.args.no); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewDuelLinks() = %v, want %v", got, tt.want)
			}
		})
	}
}
