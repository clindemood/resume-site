# Deployment

This project can be hosted on AWS in a few different ways. Below are two common approaches.

## Option A – Single container/EC2

1. Create an ECR repository and push the container image.

   ```bash
   aws ecr create-repository --repository-name resume-site --region <region>

   docker build -t resume-site:latest .
   aws ecr get-login-password --region <region> \
     | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker tag resume-site:latest <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
   ```

2. Launch the container on ECS Fargate or an EC2 instance behind an ALB.

   ```bash
   aws ecs run-task --cluster resume-cluster --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-abc],securityGroups=[sg-123],assignPublicIp=ENABLED}" \
     --task-definition resume-site
   ```

3. Configure an Application Load Balancer and target group, then expose port 80/443.

   ```bash
   aws elbv2 create-target-group --name resume-tg --protocol HTTP --port 80 --vpc-id vpc-123
   aws elbv2 register-targets --target-group-arn <tg-arn> --targets Id=<ecs-task-id>
   aws elbv2 create-listener --load-balancer-arn <lb-arn> --protocol HTTP --port 80 \
     --default-actions Type=forward,TargetGroupArn=<tg-arn>
   ```

4. Point your domain to the load balancer using Route53.

   ```bash
   aws route53 change-resource-record-sets --hosted-zone-id <zone-id> --change-batch file://dns.json
   ```

## Option B – Static hosting + serverless API

1. Upload files under `app/static/` to an S3 bucket configured for static website hosting or fronted by CloudFront.
2. Package the FastAPI app for AWS Lambda using [Mangum](https://github.com/jordaneremieff/mangum) or a similar ASGI adapter.
3. Deploy the function behind API Gateway with endpoints under `/api/*` and enable CORS for your static site's origin.
4. Update any front-end code if the API lives on a different domain.

## General notes

- Include the JSON data files in your deployment artifact so the API can load resume content.
- No external database is required; sessions are kept in memory.
- Use CloudWatch Logs or similar monitoring to track runtime errors and access logs.
