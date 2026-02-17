# ADR-002: Same AWS Account as Other Projects

## Status
Accepted

## Context
We already have infrastructure in an AWS account (umans.ai DNS, ECS clusters, etc.). We need to decide whether to use the same account or create a new one for cinematch.

## Decision
Use the **same AWS account** as other Umans projects.

## Rationale
- **Speed**: No new account setup, billing separation, or cross-account complexity
- **Shared resources**: Reuse existing DNS zone (umans.ai), certificate management, base ECS infrastructure
- **Team familiarity**: Same AWS profile, same terraform state backend setup
- **Cost**: No additional account overhead

## Implications

### Risks
- **Blast radius**: Issues in cinematch could affect other projects
- **Permissions**: Need careful IAM to prevent accidental changes to other resources
- **Cost tracking**: Harder to separate cinematch costs (use tags)

### Mitigations
- Separate Terraform workspaces (preview/production)
- Resource naming prefix: `cinematch-*`
- Tag all resources with `Project: cinematch`
- Use separate ECS cluster for cinematch services

## Date
2025-02-17
