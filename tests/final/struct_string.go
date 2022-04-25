package main

type JobResponse struct {
	Remarks string
}

func main() {
	var a JobResponse

	a.Remarks = "ohh yeaaaah"

	printf(a.Remarks)

	return
}
