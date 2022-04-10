// multidimensional array and functions and if-else

func BubbleSort(array [7]int) [7]int {
	for i := 0; i < 7; i++ {
		for j := 0; j < i; j++ {
			if array[j] > array[j+1] {
				var temp int = array[j]
				array[j] = array[j+1]
				array[j+1] = temp
			}
		}
	}
	return array
}
func main() {
	BubbleSort([7]int{11, 14, 3, 8, 18, 17, 43})

	var i int = 1
    if i == 1 {
    	j := 1
    	if j != 1 {
    	   k := 1
    	} else if j == 2 {
    	    k := 3
    	} else {
    	    k := 4
    	}
    } else if i > 1 {
    `	k := 5
    }
}
