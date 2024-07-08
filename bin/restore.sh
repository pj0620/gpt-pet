# TODO add code to copy $1/backup_config.json to $1/restore_config.json

curl -H "Content-Type: application/json"\
     "http://localhost:5000/v1/backups/s3/$1/restore"
