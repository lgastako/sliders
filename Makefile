help: ## Display this help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

SHOW:=$(shell which bat || echo "cat")
show: ## Show the Makefile
	@$(SHOW) Makefile

VIDEO_ID=xDmzbMyBKos
TRANSCRIPT_ID=AUieDaZDGqaIMRHR-3EyhpIgwLzzo2EImyehyfVVsgzNYRzI9BE

## TODO Env
YOUTUBE_API_KEY=AIzaSyCD-kz9K4IMhD23-1rBLhFxxzJGZsn4MPU

CLIENT_ID=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com
CLIENT_SECRET=d-FL95Q19q7MQmFpd7hHD0Ty
REFRESH_TOKEN=1//0dAkoN00UhEyWCgYIARAAGA0SNwF-L9IrWxN31Ft3eZXpZyJArZ2kXuaQqrVHUiZ9AyUBIKDtCD1KSWOoq31lUXlW--TRo_3eNik

ACCESS_TOKEN=ya29.a0AVvZVspLtWfyGXMMhZOzVVm23IYH6Mzvd9fuk-oqSGZBIy9k1JmCrSJOQjNS5-ms1-7H12U0l91IYxvPA4pwAtcTclTyPsurXsDa9XbqE5vcvil9eKtfPPvPLffzAWlreHY1b6ej94hOGPcq1r52H_uxVVFrZhcaCgYKAcoSARASFQGbdwaIQIIoLPrxxiriu7VHA15UTg0166

CAPTIONS_API=https://www.googleapis.com/youtube/v3/captions
CURL=curl


set-default-login-scope-stuff:
	gcloud auth application-default login

transcript-list:  ## Fetch transcript list for $(VIDEO_ID)
	$(CURL) -sSL "$(CAPTIONS_API)?videoId=$(VIDEO_ID)&part=snippet&key=$(YOUTUBE_API_KEY)" \
    | jq .

exchange-refresh-token-for-access-token:
	$(CURL) -X POST \
	  -d "client_id=$(CLIENT_ID)" \
		-d "client_secret=$(CLIENT_SECRET)" \
		-d "refresh_token=$(REFRESH_TOKEN)" \
		-d "grant_type=refresh_token" \
	https://oauth2.googleapis.com/token \
    | jq .access_token


download-transcript:  ## Download transcript by $(TRANSCRIPT_ID)
	$(CURL) -sSLH "Authorization: Bearer $(ACCESS_TOKEN)" "$(CAPTIONS_API)/$(TRANSCRIPT_ID)?key=$(YOUTUBE_API_KEY)"

