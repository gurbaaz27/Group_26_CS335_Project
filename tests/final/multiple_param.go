package main

const mod int = 900

func foo(a int , d int8 , e int16 , g float32 , h float64 , point *float32) int {
	printf(a,d,e,g,h,*point)
	*point = 90.9
}

func main() {
	var a int = 12
	var d int = 7
	var e int = 72
	var f int = 65
	var g int = 12
	var h int = 3
	var i int = 4
	var j int = 43
	fl := 9.0
	point := &float32(fl)
	printf("before function call j = ",fl)
	printf(foo(a,int8(d),int16(e),3.4,fl,point))
	printf("after function call j = ",fl)
}