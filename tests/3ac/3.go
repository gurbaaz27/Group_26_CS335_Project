// switch

func main() {
	var value string = "five"

	// Switch statement without default statement
	// Multiple values in case statement
	switch value {
	case "one":
		a := 1

	case "two", "three":
		a := 1

	case "four", "five", "six":
		a := 1
	}

	var valuen int = 2
	//switch without expression
	switch {
	case valuen == 1:
		a := 1
	case valuen == 2:
		b := 2
	case valuen == 3:
		c := 2
	default:
		d := 1
	}

	// error case  as in 2nd case type of all is not same
	switch value {
	case "one":
		a := 1

	case "two":
		a := 1

	case "four", "five", "six":
		a := 1
	}
}
