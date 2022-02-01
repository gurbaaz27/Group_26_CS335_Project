// methods and if-else

package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func CheckError(err error) {
	// catch to error.
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func HashAndSalt(pwd string) string {

	// Use GenerateFromPassword to hash & salt pwd.

	pwdbyte := []byte(pwd)
	hash, err := bcrypt.GenerateFromPassword(pwdbyte, bcrypt.MinCost)
	CheckError(err)
	log.Println("Encrypted password :", string(hash))
	/*GenerateFromPassword returns a byte slice so we need to
	convert the bytes to a string and return it*/
	return string(hash)
}

func main() {
	if num := 9; num < 0 {
		fmt.Println(num, "is negative")
	} else if num < 10 {
		fmt.Println(num, "has 1 digit")
	} else {
		fmt.Println(num, "has multiple digits")
	}
}
