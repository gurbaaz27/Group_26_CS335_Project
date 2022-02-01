// Data types and pointers
package main

import "fmt"

func zeroval(ival int) {
       ival = 0
}

func zeroptr(iptr *int) {
       *iptr = 0
}

func main() {
    x := 3 + 40E100 * 100e-10
    x = + -20 *2
    x = E-10
    x = 10.1010
    x = .0101
    x = 0.00000
    x = .1001
    x = .000011e+00001000
    x = .000e11
    x = .0000E21
    x = 100.000011e-1
    x = 100.000e10
    x = 10000.121031
    x = 0X12345
    x = 023459   // note that since 023459 is not a valid octal, our lexer breaks it to 02345 and 9
    x = 0o2324
    x = 0O23
    
    var a string = "Hello!"
    var b bool = true
    var c int64 = 3690
    var d uint8 = 97;

    i := 1
    fmt.Println("initial:", i)

    zeroval(i)
    fmt.Println("zeroval:", i)

    zeroptr(&i)
    fmt.Println("zeroptr:", i)

    fmt.Println("pointer:", &i)
}
