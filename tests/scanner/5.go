/* switch case and commenting*/

/* test
multiple line
comments */

package main

import (
	"fmt"
	"time"
)

func main() {

	i := 2
	var y int = 0x34 //*//* // /*/ /*\*/*///***/*/*/*/*/*/*///***

	/*//This is another comment//*/

	/* /* /* Check for nesting/* * *** /
	var x int = 0x34
	/////*/var x int = 0x34

	switch time.Now().Weekday() {
	case time.Saturday, time.Sunday:
		fmt.Println("It's the weekend")
	default:
		fmt.Println("It's a weekday")
	}

	t := time.Now()
	switch {
	case t.Hour() < 12:
		fmt.Println("It's before noon")
	default:
		fmt.Println("It's after noon")
	}

	whatAmI := func(i interface{}) {
		switch t := i.(type) {
		case bool:
			fmt.Println("I'm a bool")
		case int:
			fmt.Println("I'm an int")
		default:
			fmt.Printf("Don't know type %T\n", t)
		}
	}
	whatAmI(true)
	whatAmI(1)
	whatAmI("hey")

	s := "Tests for strings."
	s = " // /* */."
	s = "\n"
	s = " \"quotes\""
	s = "multi
	iqfiow
	line."
	// we have purposely added here a multi-line string, which is not supported
	// this results in our lexer giving you an illegal character error, as expected
}
