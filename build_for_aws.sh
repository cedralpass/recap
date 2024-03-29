#!/bin/zsh

# Call the AWS CLI command and store the output in a variable
aws_account=$(aws sts get-caller-identity --query Account --output text)

# Print the AWS account ID
echo "AWS Account ID: $aws_account"

# Concatenate the AWS account ID with the desired string
ecr_repository="${aws_account}.dkr.ecr.us-west-2.amazonaws.com"

# Print the ECR repository URL
echo "ECR Repository URL: $ecr_repository"

docker build -t recap-aiapi . -f Dockerfile.aws

# Log in to the ECR repository
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin "$ecr_repository"

# Tag your Docker image
docker tag recap-aiapi:latest "$ecr_repository/recap-aiapi:latest"
 
# Push the Docker image to the ECR repository
docker push "$ecr_repository/recap-aiapi:latest"

# Print a message indicating success
echo "Image published to ECR repository: $ecr_repository/recap-aiapi:latest"

# Update the ECS service with the new Docker image and force deployment
aws ecs update-service --cluster RecapAIApiCluster --service RecapAIApiService   --force-new-deployment