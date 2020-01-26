package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"github.com/dchest/uniuri"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"time"
)

const (
	url = "https://3g.dxy.cn/newh5/view/pneumonia"
)

var (
	client = http.Client{
		Timeout: time.Minute,
	}
	Logger           *log.Logger
	regex            = regexp.MustCompile(`(?m)= (.*)}catch\(`)
	enableLogger     bool
	scrapeSessionId  = uniuri.NewLen(16)
	sessionStartedAt = time.Now()
	cache            = map[string]string{}
	interval         time.Duration
	logFile          string
	folder           string
)

type ScrapeResult struct {
	Time           time.Time `json:"time"`
	Session        string    `json:"session"`
	SessionStarted time.Time `json:"session_started"`
	Content        string    `json:"content"`
}

func get() {
	Logger.Printf("fetching http resource")
	request, err := client.Get(url)
	if err != nil {
		Logger.Printf("failed to fetch http resource: %v", err)
	}
	Logger.Printf("http resource fetched")
	parse(request)
}

func parse(response *http.Response) {
	responseTime := time.Now()
	doc, err := goquery.NewDocumentFromReader(response.Body)
	if err != nil {
		Logger.Printf("failed to initialize goquery document: %v", err)
	}
	doc.Find(`script[id^="get"]`).Each(func(i int, selection *goquery.Selection) {
		id, have := selection.Attr("id")
		contents := regex.FindStringSubmatch(selection.Text())
		var content string
		if len(contents) == 2 {
			content = contents[1]
		} else {
			Logger.Printf("malformed regex result: len=%v %v", len(contents), contents)
			return
		}
		if len(content) != 0 && have {
			hashBytes := sha256.Sum256([]byte(content))
			hashString := hex.EncodeToString(hashBytes[:])
			cacheHash, ok := cache[id]
			if ok {
				// have cache. compare if is new or not
				if hashString == cacheHash {
					// not updated. skip saving
					return
				} // else: updated. do saving.
			} else {
				// first run. save data.
				Logger.Printf("(cache) first time running the app. saving both content and cache")
			}

			filePath := filepath.Join(folder, id+".jsonl")
			fmt.Println(filePath)
			file, err := os.OpenFile(filePath, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0664)
			if err != nil {
				Logger.Printf("failed to open data file: %v", err)
				return
			}
			defer file.Close()

			result := ScrapeResult{
				Time:           responseTime,
				Session:        scrapeSessionId,
				SessionStarted: sessionStartedAt,
				Content:        content,
			}
			bytes, err := json.Marshal(result)
			if err != nil {
				Logger.Printf("failed to marshal json data: %v", err)
				return
			}
			content = string(bytes) + "\n"
			_, err = file.WriteString(content)
			if err != nil {
				Logger.Printf("failed to write to data file: %v", err)
				return
			} else {
				Logger.Printf("successfully saved data to: %v", filePath)
			}

			// save current result to cache
			cache[id] = hashString
		} else {
			Logger.Printf("suspected malformed data. len(content): %v, have id attr: %v", len(content), have)
		}
	})
}

func main() {
	flag.BoolVar(&enableLogger, "logger", true, "enable logger or not. if set to false, program will write log to /dev/null. if set to true, program will write log to logfile")
	flag.StringVar(&logFile, "log", "runtime.log", "path of the log file")
	flag.StringVar(&folder, "path", "data/", "path to put the data files")
	flag.DurationVar(&interval, "interval", time.Minute, "interval between http requests")
	flag.Parse()

	var file *os.File
	if enableLogger {
		var err error
		file, err = os.OpenFile(logFile, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0664)
		if err != nil {
			log.Printf("failed to open log file %v", err)
		}
		defer file.Close()
	} else {
		var err error
		file, err = os.OpenFile("/dev/null", os.O_RDWR|os.O_APPEND, 0664)
		if err != nil {
			log.Printf("failed to open log file %v", err)
		}
		defer file.Close()
	}
	Logger = log.New(file, "[main] ", log.LstdFlags)

	err := os.MkdirAll(folder, 0755)
	if err != nil {
		Logger.Printf("failed to create folder: %v", err)
	}

	rand.Seed(time.Now().UnixNano())
	ticker := time.NewTicker(interval)
	get()

	for {
		select {
		case <-ticker.C:
			get()
		}
	}
}
