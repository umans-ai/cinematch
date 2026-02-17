# ADR-005: Infrastructure Isolation from llm-gateway

## Status
Accepted

## Context
CineMatch shares the same AWS account as llm-gateway. We need to ensure complete isolation to prevent any impact on llm-gateway production.

## Decision
Implement STRICT ISOLATION at every layer:

### Network Isolation
- Dedicated VPC for CineMatch (10.1.0.0/16)
- Different from llm-gateway (10.0.0.0/16)
- Own subnets, route tables, internet gateway

### Resource Isolation
- Dedicated ECS Cluster named "cinematch" (not shared)
- Dedicated ECR repositories
- Dedicated Security Groups (prefixed with "cinematch-")
- Dedicated IAM Roles (prefixed with "cinematch-")
- Dedicated CloudWatch Log Groups

### Shared Resources (READ-ONLY)
Only the Route53 zone "umans.ai" is shared (org-level resource)
Everything else is created specifically for CineMatch

## Red Lines (MUST NOT)
- MUST NOT reference llm-gateway resources (except Route53 zone data)
- MUST NOT share ECS clusters
- MUST NOT share ALBs
- MUST NOT share security groups
- MUST NOT share IAM roles
- MUST use force_delete = true on ECR for easy cleanup

## Consequences
- Higher resource count (but minimal cost for small ECS)
- Complete isolation = destroy cinematch without impacting llm-gateway
- Slightly more complex (but safer)

## Verification
Before any destroy operation:
1. Check terraform plan shows only cinematch resources
2. Verify no references to llm-gateway outputs
3. Confirm separate VPC CIDR blocks

## Date
2025-02-17
