import hre from "hardhat";
const { ethers } = hre;
import { expect } from "chai";

describe("AuditEventRegistry", function () {
  let AuditEventRegistry;
  let registry;
  let deployer, addr1, addr2;

  before(async function () {
    [deployer, addr1, addr2] = await ethers.getSigners();
    AuditEventRegistry = await ethers.getContractFactory("AuditEventRegistry");
  });

  beforeEach(async function () {
    registry = await AuditEventRegistry.deploy();
    await registry.waitForDeployment();
  });

  // Helper to decode AuditEvent struct from getEvent
  // ethers v6 decodeFunctionResult returns nested array for tuple returns
  async function getEventByIndex(index) {
    const data = registry.interface.encodeFunctionData("getEvent", [index]);
    const result = await hre.ethers.provider.call({
      to: await registry.getAddress(),
      data
    });
    const decoded = registry.interface.decodeFunctionResult("getEvent", result);
    // decoded is [tuple] where tuple = [eventType, policyId, commitmentHash, committedAt, committedBy]
    return decoded[0];
  }

  describe("Deployment", function () {
    it("Should start with zero events", async function () {
      expect(await registry.getEventCount()).to.equal(0);
    });
  });

  describe("recordEvent", function () {
    const eventType = ethers.id("BIND");
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should record an event and return the index", async function () {
      const tx = await registry.recordEvent(eventType, policyId, commitmentHash);
      await tx.wait();
      expect(await registry.getEventCount()).to.equal(1);
    });

    it("Should emit AuditEventRecorded event", async function () {
      const tx = await registry.recordEvent(eventType, policyId, commitmentHash);
      await tx.wait();
      await expect(tx).to.emit(registry, "AuditEventRecorded");
    });

    it("Should store correct event data", async function () {
      await registry.recordEvent(eventType, policyId, commitmentHash);
      const event = await getEventByIndex(0);
      expect(event[0]).to.equal(eventType);       // eventType
      expect(event[1]).to.equal(policyId);        // policyId
      expect(event[2]).to.equal(commitmentHash);  // commitmentHash
      expect(event[4]).to.equal(deployer.address); // committedBy
      expect(event[3]).to.be.greaterThan(0);       // committedAt
    });

    it("Should allow multiple events from different senders", async function () {
      await registry.connect(deployer).recordEvent(eventType, policyId, commitmentHash);
      await registry.connect(addr1).recordEvent(eventType, policyId, commitmentHash);
      expect(await registry.getEventCount()).to.equal(2);
      const evt0 = await getEventByIndex(0);
      const evt1 = await getEventByIndex(1);
      expect(evt0[4]).to.equal(deployer.address);
      expect(evt1[4]).to.equal(addr1.address);
    });
  });

  describe("getEvent", function () {
    const eventType = ethers.id("BIND");
    const policyId = ethers.id("POL-001");
    const commitmentHash = ethers.id("audit-packet-001");

    it("Should revert on out-of-bounds index", async function () {
      const data = registry.interface.encodeFunctionData("getEvent", [999]);
      await expect(
        hre.ethers.provider.call({ to: await registry.getAddress(), data })
      ).to.be.revertedWith("AuditEventRegistry: index out of bounds");
    });

    it("Should return correct event after recording", async function () {
      await registry.recordEvent(eventType, policyId, commitmentHash);
      const event = await getEventByIndex(0);
      expect(event[0]).to.equal(eventType);
    });
  });

  describe("getEventsByPolicy", function () {
    const policyId = ethers.id("POL-001");
    const bindType = ethers.id("BIND");
    const cancelType = ethers.id("CANCELLATION");
    const hash1 = ethers.id("audit-001");
    const hash2 = ethers.id("audit-002");
    const otherPolicy = ethers.id("POL-999");

    it("Should return events for a specific policy", async function () {
      await registry.recordEvent(bindType, policyId, hash1);
      await registry.recordEvent(cancelType, policyId, hash2);
      await registry.recordEvent(bindType, otherPolicy, ethers.id("audit-999"));

      const indices = await registry.getPolicyEvents(policyId);
      expect(indices.length).to.equal(2);
    });

    it("Should return empty array for policy with no events", async function () {
      const indices = await registry.getPolicyEvents(otherPolicy);
      expect(indices.length).to.equal(0);
    });
  });

  describe("getEventsByType", function () {
    const policyId = ethers.id("POL-001");
    const bindType = ethers.id("BIND");
    const cancelType = ethers.id("CANCELLATION");
    const hash1 = ethers.id("audit-001");
    const hash2 = ethers.id("audit-002");
    const hash3 = ethers.id("audit-003");

    it("Should return events of a specific type", async function () {
      await registry.recordEvent(bindType, policyId, hash1);
      await registry.recordEvent(cancelType, policyId, hash2);
      await registry.recordEvent(bindType, policyId, hash3);

      const indices = await registry.getEventsByType(bindType);
      expect(indices.length).to.equal(2);
    });

    it("Should return empty array for type with no events", async function () {
      const renewalType = ethers.id("RENEWAL");
      const indices = await registry.getEventsByType(renewalType);
      expect(indices.length).to.equal(0);
    });
  });

  describe("Append-only behavior", function () {
    const eventType = ethers.id("BIND");
    const policyId = ethers.id("POL-001");
    const hash1 = ethers.id("audit-001");
    const hash2 = ethers.id("audit-002");

    it("Should allow multiple events at different indices", async function () {
      await registry.recordEvent(eventType, policyId, hash1);
      await registry.recordEvent(eventType, policyId, hash2);
      expect(await registry.getEventCount()).to.equal(2);
      const evt0 = await getEventByIndex(0);
      const evt1 = await getEventByIndex(1);
      expect(evt0[2]).to.equal(hash1);
      expect(evt1[2]).to.equal(hash2);
    });

    it("Should preserve event order", async function () {
      for (let i = 0; i < 5; i++) {
        const hash = ethers.id(`audit-${i}`);
        await registry.recordEvent(eventType, policyId, hash);
      }
      expect(await registry.getEventCount()).to.equal(5);
      for (let i = 0; i < 5; i++) {
        const event = await getEventByIndex(i);
        expect(event[0]).to.equal(eventType);
        expect(event[1]).to.equal(policyId);
      }
    });
  });

  describe("All event types", function () {
    const policyId = ethers.id("POL-001");
    const eventTypes = [
      "BIND",
      "ENDORSEMENT",
      "CANCELLATION",
      "RENEWAL",
      "CLAIM_FILING",
      "CLAIM_SETTLEMENT"
    ];

    it("Should record all event types correctly", async function () {
      for (let i = 0; i < eventTypes.length; i++) {
        const eventType = ethers.id(eventTypes[i]);
        const hash = ethers.id(`audit-${eventTypes[i]}`);
        await registry.recordEvent(eventType, policyId, hash);
      }
      expect(await registry.getEventCount()).to.equal(eventTypes.length);
    });
  });
});
