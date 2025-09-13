# Deployment

This project can be hosted on AWS in a few different ways. Below are two common approaches.

## Option A – Single container/EC2

1. Build the included `Dockerfile` and push the image to Amazon ECR.
2. Run the container on ECS Fargate or an EC2 instance behind an ALB.
3. Expose port 80/443 and point your domain to the load balancer.

## Option B – Static hosting + serverless API

1. Upload files under `app/static/` to an S3 bucket configured for static website hosting or fronted by CloudFront.
2. Package the FastAPI app for AWS Lambda using [Mangum](https://github.com/jordaneremieff/mangum) or a similar ASGI adapter.
3. Deploy the function behind API Gateway with endpoints under `/api/*` and enable CORS for your static site's origin.
4. Update any front-end code if the API lives on a different domain.

## General notes

- Include the JSON data files in your deployment artifact so the API can load resume content.
- No external database is required; sessions are kept in memory.
- Use CloudWatch Logs or similar monitoring to track runtime errors and access logs.
