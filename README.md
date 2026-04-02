# demo-scraper-repo

                ┌──────────────────────────────┐
                │         GitHub Repo          │
                │  (Scraper code + Terraform)  │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │        AWS CodePipeline      │
                │     (CI/CD Orchestration)    │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │        AWS CodeBuild         │
                │   Build Docker Image         │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │            AWS ECR           │
                │   Store Scraper Docker Image │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │      ECS Task Definition     │
                │  (uses latest scraper image) │
                └──────────────────────────────┘


                ┌──────────────────────────────┐
                │       Amazon EventBridge     │
                │    (Schedule / Trigger)      │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │      AWS Step Functions      │
                │ Retry / Orchestration / Flow │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │       Amazon ECS Fargate     │
                │   Runs Playwright Scraper    │
                └──────────────┬───────────────┘
                               │
               ┌───────────────┴────────────────┐
               │                                │
               ▼                                ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│         Amazon DynamoDB      │   │            Amazon S3         │
│       Store Raw Scraped      │   │    Store Final CSV Export    │
│            Records           │   │                              │
└──────────────────────────────┘   └──────────────────────────────┘
