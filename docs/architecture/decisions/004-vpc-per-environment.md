# ADR 004: VPC Per Environment

## Status
Accepted

## Context
Current infrastructure has VPC defined in `00-foundation`, shared across all environments. This breaks our philosophy of:

1. **Répétabilité**: A preview should be an exact replica of production
2. **Isolation**: Environments should not share network infrastructure
3. **Fast feedback**: Network issues in one env shouldn't affect others

The foundation/service split was:
- **00-foundation**: VPC, ECR, ACM, Route53 (shared, rarely changes)
- **01-service**: ECS, ALB, per environment (workspace-based)

But VPC is environment-specific, not shared.

## Decision
**VPC moves from foundation to per-environment (01-service).**

Each `terraform workspace` (preview-123, staging, production) creates its own completely isolated VPC.

### Why Not Keep Shared VPC?

**Against our principles:**
- Convergence: All envs share same network addressing, routing, security groups
- False confidence: Preview doesn't test "real" network topology
- Blast radius: Network misconfiguration in preview affects production
- State coupling: Foundation change affects all environments simultaneously

**Operational risk:**
- "Works in preview, fails in prod" due to network differences
- Hard to test network-level changes safely

### Migration Strategy

**Phase 1: Dual-Path (Immediate)**
```
01-service/vpc.tf       # NEW: VPC per workspace
01-service/rds.tf       # NEW: RDS in per-env VPC
operations/00-foundation/vpc.tf  # KEEP temporarily for existing prod
```

- New previews use VPC in 01-service
- Existing production stays on foundation VPC (no forced migration)

**Phase 2: Production Migration (Planned)**
When ready:
1. Create production workspace VPC in 01-service
2. Provision new RDS, migrate data
3. Blue-green: Switch Route53 to new ALB
4. Decommission old foundation resources

**Phase 3: Foundation Cleanup**
Remove VPC from foundation once production migrated.

### New Foundation Scope
Truly shared, environment-agnostic resources only:
- ECR repositories (images are shared)
- Route53 zone (DNS root)
- ACM certificate (wildcard for all subdomains)

## Consequences

### Positive
- **True reproducibility**: Preview network = production network
- **Complete isolation**: Network issues don't cross environments
- **Safe experimentation**: Can modify network in preview without fear
- **Parallel changes**: Different envs can have different network configs during migration

### Negative
- **Cost**: Multiple VPCs (but VPC itself is free, only resources cost)
- **Complexity**: More moving parts initially
- **Migration effort**: Need to move existing production eventually

### Mitigations
- **Cost**: Preview VPCs are ephemeral (live hours/days, not months)
- **Complexity**: Abstracted by Terraform modules
- **Migration**: Deferred until convenient, no forced timeline

## Implementation

```hcl
# 01-service/vpc.tf
resource "aws_vpc" "cinematch" {
  cidr_block = "10.${terraform.workspace == "production" ? 1 : random_id.network_offset.dec}.0.0/16"

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}
```

Each workspace gets distinct CIDR range to avoid conflicts if VPN peering ever needed.

## References
- [AWS VPC Limits](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html)
- [Terraform Workspace Pattern](https://developer.hashicorp.com/terraform/language/state/workspaces)
