package main


const a int = 5
const b int = 6
const c int = 7
const d int = 8



var	x int = a + c
var y int = 6
var z int

func main() {
	var g int = 5
	g += 6

	switch (g) {
	case 5:
		g++
	case 12:
		g--
	default:
		g = 11
	}
	printf(x,y,g)
}