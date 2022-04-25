package main


func getVal2(a int, b int) int {
	return 10 + a + b
}

func getVal() int {
	return 8 + getVal2(17, 45)
}

func main() {
	printf(getVal())
}