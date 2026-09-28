package utils

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
)

type sseUtil struct {
}

type ServerSendEvent struct {
	Data  string `json:"data"`
	Event string `json:"event"`
	Id    string `json:"id"`
}
type SseRequest struct {
	url    string
	method string
	body   map[string]any
}

var SSE sseUtil

func (*sseUtil) New() *SseRequest {
	return &SseRequest{}
}

func (r *SseRequest) SetMethod(method string) *SseRequest {
	r.method = method
	return r
}

func (r *SseRequest) SetUrl(url string) *SseRequest {
	r.url = url
	return r
}

func (r *SseRequest) SetBody(body map[string]any) *SseRequest {
	r.body = body
	return r
}

func (r *SseRequest) Execute(handler func(event ServerSendEvent)) error {
	client := resty.New()

	resp, err := client.R().
		SetDoNotParseResponse(true).
		SetBody(r.body).
		Execute(r.method, r.url)

	if err != nil {
		return err
	}

	body := resp.RawBody()
	defer func() {
		err := body.Close()
		if err != nil {
			slog.Error("关闭流错误", "SSEError", err)
		}
	}()

	reader := bufio.NewReader(body)
	var currentEvent ServerSendEvent

	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			if errors.Is(err, io.EOF) {
				if currentEvent.hasContent() {
					handler(currentEvent)
				}
				break
			}
			slog.Error("读取流错误", "SseUtil", err)
			return fmt.Errorf("读取流错误 %w", err)
		}

		line = strings.TrimSpace(line)
		if line == "" {
			if currentEvent.hasContent() {
				handler(currentEvent)
				currentEvent = ServerSendEvent{}
			}
			continue
		}
		updateEventFromLine(line, &currentEvent)
	}

	return nil
}

func (r *SseRequest) StreamWithHandler(c *gin.Context, handler func(c *gin.Context, event ServerSendEvent)) {
	clientGone := c.Writer.CloseNotify()
	var continueProcessing = true

	err := r.Execute(func(event ServerSendEvent) {
		if !continueProcessing {
			return
		}

		select {
		case <-clientGone:
			continueProcessing = false
			return
		default:
			handler(c, event)
		}
	})

	if err != nil {
		slog.Error("SSE执行出错", "SSEError", err)
		Resp.StreamError(c)
		c.Writer.Flush()
	}
}

func (r *SseRequest) Stream(c *gin.Context) {
	r.StreamWithHandler(c, func(c *gin.Context, event ServerSendEvent) {
		c.SSEvent(event.Event, event.Data)
		c.Writer.Flush()
	})
}

func updateEventFromLine(line string, event *ServerSendEvent) {
	switch {
	case strings.HasPrefix(line, "data:"):
		data := strings.TrimPrefix(line, "data:")
		if event.Data == "" {
			event.Data = data
		} else {
			event.Data += "\n" + data
		}
	case strings.HasPrefix(line, "event:"):
		event.Event = strings.TrimPrefix(line, "event:")
	case strings.HasPrefix(line, "id:"):
		event.Id = strings.TrimPrefix(line, "id:")
	}
}

func (e *ServerSendEvent) hasContent() bool {
	return e.Data != "" || e.Event != "" || e.Id != ""
}
