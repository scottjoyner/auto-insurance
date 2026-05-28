import hre from "hardhat";
const { ethers } = hre;
import { expect } from "chai";

describe("PolicyRegistry", function () {
  let PolicyRegistry;
  let registry;
  let deployer, addr1, addr2;

  before(async function () {
    [deployer, addr1, addr2] = await ethers.getSigners();
    PolicyRegistry = await ethers.getContractFactory("PolicyRegistry");
  });

  beforeEach(async function () {
    registry = await PolicyRegistry.deploy();
    await registry.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct policy count", async function () {
      expect(await registry.getPolicyCount()).to.equal(0);
    });

    it("Should have a valid address", async function () {
      expect(await registry.getAddress()).to.not.be.empty;
    });
  });

  describe("commitPolicy", function () {
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should commit a new policy", async function () {
      const tx = await registry.commitPolicy(policyId, commitmentHash, 1); // ACTIVE
      await tx.wait();
      expect(await registry.getPolicyCount()).to.equal(1);
    });

    it("Should emit PolicyCommitted event", async function () {
      const tx = await registry.commitPolicy(policyId, commitmentHash, 1);
      await tx.wait();
      await expect(tx)
        .to.emit(registry, "PolicyCommitted");
    });

    it("Should revert on duplicate policy commit", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      await expect(
        registry.commitPolicy(policyId, commitmentHash, 1)
      ).to.be.revertedWith("PolicyRegistry: policy already committed");
    });

    it("Should store correct record data", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      const record = await registry.getPolicy(policyId);
      expect(record.policyId).to.equal(policyId);
      expect(record.commitmentHash).to.equal(commitmentHash);
      expect(record.status).to.equal(1); // ACTIVE
      expect(record.committedBy).to.equal(deployer.address);
    });

    it("Should add policy to enumeration array", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      expect(await registry.getPolicyByIndex(0)).to.equal(policyId);
    });
  });

  describe("updatePolicyStatus", function () {
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should update policy status", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1); // ACTIVE
      await registry.updatePolicyStatus(policyId, 4); // EXPIRED
      expect(await registry.getPolicyStatus(policyId)).to.equal(4);
    });

    it("Should emit PolicyStatusUpdated event", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      const tx = await registry.updatePolicyStatus(policyId, 4);
      await tx.wait();
      await expect(tx)
        .to.emit(registry, "PolicyStatusUpdated");
    });

    it("Should revert if policy does not exist", async function () {
      const fakeId = ethers.id("NONEXISTENT");
      await expect(
        registry.updatePolicyStatus(fakeId, 1)
      ).to.be.revertedWith("PolicyRegistry: policy not found");
    });
  });

  describe("policyExists", function () {
    const policyId = ethers.id("POL-001");

    it("Should return false for non-existent policy", async function () {
      expect(await registry.policyExists(policyId)).to.be.false;
    });

    it("Should return true after commit", async function () {
      const commitmentHash = ethers.id("audit-packet-001");
      await registry.commitPolicy(policyId, commitmentHash, 1);
      expect(await registry.policyExists(policyId)).to.be.true;
    });
  });

  describe("getCommitmentHash", function () {
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should return correct commitment hash", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      expect(await registry.getCommitmentHash(policyId)).to.equal(commitmentHash);
    });

    it("Should revert for non-existent policy", async function () {
      const fakeId = ethers.id("NONEXISTENT");
      await expect(registry.getCommitmentHash(fakeId))
        .to.be.revertedWith("PolicyRegistry: policy not found");
    });
  });

  describe("getCommittedAt", function () {
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should return non-zero timestamp", async function () {
      await registry.commitPolicy(policyId, commitmentHash, 1);
      const timestamp = await registry.getCommittedAt(policyId);
      expect(timestamp).to.be.greaterThan(0);
    });
  });

  describe("getPolicyByIndex", function () {
    const id1 = ethers.id("POL-001");
    const id2 = ethers.id("POL-002");
    const hash1 = ethers.id("audit-001");
    const hash2 = ethers.id("audit-002");

    it("Should return policies in insertion order", async function () {
      await registry.commitPolicy(id1, hash1, 1);
      await registry.commitPolicy(id2, hash2, 1);
      expect(await registry.getPolicyByIndex(0)).to.equal(id1);
      expect(await registry.getPolicyByIndex(1)).to.equal(id2);
    });

    it("Should revert on out-of-bounds index", async function () {
      await expect(registry.getPolicyByIndex(999))
        .to.be.revertedWith("PolicyRegistry: index out of bounds");
    });
  });

  describe("Multiple policies", function () {
    it("Should handle multiple commits and status updates", async function () {
      const p1 = ethers.id("POL-A");
      const p2 = ethers.id("POL-B");
      const h1 = ethers.id("audit-a");
      const h2 = ethers.id("audit-b");

      await registry.commitPolicy(p1, h1, 1); // ACTIVE
      await registry.commitPolicy(p2, h2, 0); // PENDING

      expect(await registry.getPolicyCount()).to.equal(2);
      expect(await registry.getPolicyStatus(p1)).to.equal(1);
      expect(await registry.getPolicyStatus(p2)).to.equal(0);

      await registry.updatePolicyStatus(p1, 3); // CANCELLED
      expect(await registry.getPolicyStatus(p1)).to.equal(3);
    });
  });
});
