package main

type WebServer struct {
	Port   int64
	Status  string
	Children [8]int64
}

func main() {
	var ws WebServer
	ws.Port = 8000
	ws.Port += 80
	ws.Status = "Server Up and Working"

	for i := 0; i < 8 ; i++ {
		ws.Children[i] = i
	}

	printf(ws.Port)
	printf(ws.Status)

	for i := 0; i < 8 ; i++ {
		printf(ws.Children[i])
	}

	return
}
