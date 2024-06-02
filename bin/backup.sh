curl  -H "Content-Type: application/json" -d "{\"id\": \"$(date +%Y%m%d_%H%M%S)\"}" http://localhost:5000/v1/backups/s3
