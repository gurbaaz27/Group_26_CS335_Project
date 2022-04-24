package main


func main() {
   array:= [11]int{11, 14, 3, 8, 18, 17, 43 , 902 , 837 , 73838,902};

   for i := 11; i > 0; i-- {
	for j := 1; j < i; j++ {
	   if array[j-1] > array[j] {
		  intermediate := array[j]
		  array[j] = array[j-1]
		  array[j-1] = intermediate
					  }
		   }
	}

 for i:=0 ; i<11 ;i++{
	 printf(array[i])
 }
}