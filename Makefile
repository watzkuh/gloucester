USER = user
HOST = ras.local
DESTINATION_PATH = /home/path

.PHONY: copy

copy:
	scp main.py requirements.txt $(USER)@$(HOST):$(DESTINATION_PATH)

setup: copy
	ssh $(USER)@$(HOST) "mkdir -p $(DESTINATION_PATH) && cd $(DESTINATION_PATH) && pip3 install -r requirements.txt"
