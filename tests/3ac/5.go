type bed struct {
	name    string
	objects [4][5][6]int
}

type room struct {
	beds  [4]bed
	cs345 float32
}

type home struct {
	rooms   [1][2]room
	bunglos [2][3]room
	cs345   int
}

type hawk struct {
	name   string
	age    int64
	weight float32
}

type hawkeyes struct {
	g      hawk
	name   string
	age    int64
	weight float64
}

func main() {
	var house home
	house.rooms[2][3].beds[3].name
	// house.rooms[2][3].beds[3].objects[2][1] = [4]int{1, 2, 2, 2}

}
