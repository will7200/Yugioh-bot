package dl

import (
	"encoding/xml"
	"fmt"
	"image"
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

var xmlTestString = `
<?xml version="1.0" encoding="UTF-8" ?>
<Predefined>
	<Locations>
		<Location key="quick_rank_duel">
			<PropertyName>Quick RankDuels</PropertyName>
			<Description></Description>
			<PageLocation>2</PageLocation>
		</Location>
		<Location key="street_replay">
			<PropertyName>Street Replay</PropertyName>
			<Description></Description>
			<PageLocation>4</PageLocation>
		</Location>
	</Locations>
	<AssetMap>
		<Asset key="start_screen">
			<Name>start_screen.png</Name>
		</Asset>
	</AssetMap>
</Predefined>`

func Test_XMLParser(t *testing.T) {
	v := &Predefined{}
	err := xml.Unmarshal([]byte(xmlTestString), &v)
	assert.Nil(t, err)
	fmt.Printf("%#v\n", v)
	_ = &Predefined{
		Locations: []Location{{PageLocation: 4, basePredefined: basePredefined{Key: "taken"}}},
	}
	nn := image.Pt(100, 100)
	enc := xml.NewEncoder(os.Stdout)
	enc.Indent("  ", "    ")
	if err := enc.Encode(nn); err != nil {
		fmt.Printf("error: %v\n", err)
	}
}
