package main

type JobStatusResponse struct {
	// JobId   int64
	// Status  int64
	// Message float64
	Remarks string
}

func main() {
	var a JobStatusResponse
	// a.JobId = 22
	// a.Status = 98
	// a.Message = 22.5
	a.Remarks = "ohh yeaaaah"
	// var c string = "hello"
	// printf(a.Status)
	// printf(a.JobId)
	// printf(a.Message)
	const b string = a.Remarks 
	printf(b)

	return
}
