#!/bin/zsh

# login to digitalocean 
doctl registry login



# Concatenate the AWS account ID with the desired string
do_repository="registry.digitalocean.com/recap-ai-api"

# Print the ECR repository URL
echo "ECR Repository URL: $do_repository"

#docker build -t recap-aiapi . -f Dockerfile.aws

# Tag your Docker image
docker tag recap-aiapi:latest "$do_repository/recap-aiapi:latest"
 
# Push the Docker image to the DO repository
docker push "$do_repository/recap-aiapi:latest"