// +build windows

package dl

import (
	"reflect"
	"syscall"
	"testing"
)

func TestEnumWindows(t *testing.T) {
	type args struct {
		enumFunc uintptr
		lparam   uintptr
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := EnumWindows(tt.args.enumFunc, tt.args.lparam); (err != nil) != tt.wantErr {
				t.Errorf("EnumWindows() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestGetWindowText(t *testing.T) {
	type args struct {
		hwnd     syscall.Handle
		str      *uint16
		maxCount int32
	}
	tests := []struct {
		name    string
		args    args
		wantLen int32
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotLen, err := GetWindowText(tt.args.hwnd, tt.args.str, tt.args.maxCount)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetWindowText() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if gotLen != tt.wantLen {
				t.Errorf("GetWindowText() = %v, want %v", gotLen, tt.wantLen)
			}
		})
	}
}

func TestFindWindow(t *testing.T) {
	type args struct {
		title string
	}
	tests := []struct {
		name    string
		args    args
		want    syscall.Handle
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := FindWindow(tt.args.title)
			if (err != nil) != tt.wantErr {
				t.Errorf("FindWindow() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("FindWindow() = %v, want %v", got, tt.want)
			}
		})
	}
}
