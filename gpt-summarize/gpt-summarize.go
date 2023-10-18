package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"
	"unicode"

	"github.com/rakyll/openai-go"
	"github.com/rakyll/openai-go/chat"
)

var apiKey = os.Getenv("OPENAI_API_KEY")

func main() {
	gptFlag := flag.String("gpt", "gpt-4", "GPT model version to use.")
	llmPromptFlag := flag.String("llm-prompt", "", "LLM prompt for GPT model.")
	flag.Parse()

	if flag.NArg() != 1 {
		log.Fatalf("Usage: %s <filename>", os.Args[0])
	}

	filePath := flag.Args()[0]
	gptModel := *gptFlag

	data, err := os.ReadFile(filePath)
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	content := string(data)
	words := splitWords(content)
	chunks := splitIntoChunks(words, 3000)

	var summarizedChunks []string
	for _, chunk := range chunks {
		var summary string
		var err error
		summary, err = GenSummaryWithChatGPT(strings.Join(chunk, " "), gptModel, *llmPromptFlag)
		if err != nil {
			log.Println("Error generating summary: ", err)
		}

		summarizedChunks = append(summarizedChunks, summary)
	}

	fmt.Println()
	fmt.Println(strings.Join(summarizedChunks, " "))
}

func splitWords(text string) []string {
	f := func(c rune) bool {
		return unicode.IsSpace(c)
	}

	return strings.FieldsFunc(text, f)
}

func splitIntoChunks(words []string, maxWords int) [][]string {
	var chunks [][]string
	wordsLen := len(words)

	for i := 0; i < wordsLen; i += maxWords {
		end := i + maxWords

		if end > wordsLen {
			end = wordsLen
		}

		chunks = append(chunks, words[i:end])
	}

	return chunks
}

func GenSummaryWithChatGPT(text, gpt, llmPrompt string) (string, error) {
	ctx := context.Background()
	s := openai.NewSession(apiKey)
	s.HTTPClient.Timeout = 120 * time.Second

	client := chat.NewClient(s, gpt)
	resp, err := client.CreateCompletion(ctx, &chat.CreateCompletionParams{
		Messages: []*chat.Message{
			{Role: "system", Content: llmPrompt},
			{Role: "user", Content: "Please summarize this text:" + text},
		},
	})
	if err != nil {
		log.Println("GenSummaryWithChatGPT: Failed to complete:", err)
		return "", err
	}

	return resp.Choices[0].Message.Content, nil
}
