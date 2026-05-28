/**
 * @notice Deploy PolicyRegistry and AuditEventRegistry to Hardhat local network.
 * @dev Run with: npx hardhat run scripts/deploy-local.js --network hardhat
 */

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("Deploying contracts to Hardhat local network...");

  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  // Deploy PolicyRegistry
  const PolicyRegistry = await ethers.getContractFactory("PolicyRegistry");
  const policyRegistry = await PolicyRegistry.deploy();
  await policyRegistry.waitForDeployment();
  console.log("PolicyRegistry deployed to:", await policyRegistry.getAddress());

  // Deploy AuditEventRegistry
  const AuditEventRegistry = await ethers.getContractFactory("AuditEventRegistry");
  const auditEventRegistry = await AuditEventRegistry.deploy();
  await auditEventRegistry.waitForDeployment();
  console.log("AuditEventRegistry deployed to:", await auditEventRegistry.getAddress());

  // Verify deployment
  console.log("\nDeployment Summary:");
  console.log("  PolicyRegistry:    ", await policyRegistry.getAddress());
  console.log("  AuditEventRegistry:", await auditEventRegistry.getAddress());
  console.log("  Deployer:          ", deployer.address);

  // Save deployment info
  const deploymentInfo = {
    network: "hardhat",
    chainId: 31337,
    deployer: deployer.address,
    contracts: {
      PolicyRegistry: await policyRegistry.getAddress(),
      AuditEventRegistry: await auditEventRegistry.getAddress(),
    },
  };

  if (!fs.existsSync("deployments")) {
    fs.mkdirSync("deployments");
  }

  fs.writeFileSync(
    "deployments/hardhat.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to deployments/hardhat.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
