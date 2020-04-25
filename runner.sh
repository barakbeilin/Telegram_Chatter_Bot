#!/bin/bash
result=$(ps aux | grep -i -c "python src/run_bot_thread.py")

if [ $result -ge 2 ]; then
  echo "Process is running."
else
  echo "Process is not running."
fi