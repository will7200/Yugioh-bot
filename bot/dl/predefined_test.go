package dl

import (
	"encoding/xml"
	"fmt"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestLocation_String(t *testing.T) {
	type fields struct {
		basePredefined basePredefined
		PageLocation   int
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := Location{
				basePredefined: tt.fields.basePredefined,
				PageLocation:   tt.fields.PageLocation,
			}
			if got := l.String(); got != tt.want {
				t.Errorf("Location.String() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_XMLParser(t *testing.T) {
	v := &Predefined{}
	xmlTest := box.Bytes("data.xml")
	err := xml.Unmarshal(xmlTest, &v)
	assert.Nil(t, err)
	fmt.Printf("%#v\n", v)
	_ = &Predefined{
		Locations: []Location{{PageLocation: 4, basePredefined: basePredefined{Key: "taken"}}},
	}
	tv := &BotConst{}
	tv.CirclesDefinitions = CirclesDefinitions{
		215, 255, HoughCirclesDefinitions{
			1, 45, 50, 30, 3, 60,
		},
	}
	enc := xml.NewEncoder(os.Stdout)
	enc.Indent("  ", "    ")
	if err := enc.Encode(tv); err != nil {
		fmt.Printf("error: %v\n", err)
	}
}
