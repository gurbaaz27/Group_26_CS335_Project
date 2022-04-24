package main

type JobStatusResponse struct {
	JobId   int64
	Status  int64
	Message float64
	// Remarks string
}

func main() {
	var a JobStatusResponse
	a.JobId = 22
	a.Status = 98
	a.Message = 22.5
	// a.Remarks = "hello"
	printf(a.JobId)

	return
}
