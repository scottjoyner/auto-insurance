// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title PolicyRegistry
 * @notice Registry for insurance policy commitments on-chain.
 *         Only stores policy_id, commitment_hash, status, committed_at.
 *         Customer data is NEVER stored on-chain.
 */
contract PolicyRegistry {
    struct PolicyRecord {
        bytes32 policyId;           // Hash of policy_id string
        bytes32 commitmentHash;     // SHA-256 of audit packet
        PolicyStatus status;        // Current policy status
        uint256 committedAt;        // Timestamp of commitment
        address committedBy;        // Address that committed
    }

    enum PolicyStatus {
        PENDING,
        ACTIVE,
        ENDORSEMENT,
        CANCELLED,
        EXPIRED
    }

    // Mapping from policy hash to record
    mapping(bytes32 => PolicyRecord) private _records;

    // Array of all policy hashes (for enumeration)
    bytes32[] private _allPolicyIds;

    // Events
    event PolicyCommitted(
        bytes32 indexed policyId,
        bytes32 commitmentHash,
        PolicyStatus status,
        uint256 committedAt,
        address committedBy
    );

    event PolicyStatusUpdated(
        bytes32 indexed policyId,
        PolicyStatus newStatus,
        uint256 updatedAt,
        address updatedBy
    );

    // Modifiers
    modifier onlyPolicyExists(bytes32 policyId) {
        require(_records[policyId].committedAt > 0, "PolicyRegistry: policy not found");
        _;
    }

    // -----------------------------------------------------------------------
    // Public functions
    // -----------------------------------------------------------------------

    /**
     * @notice Commit a new policy to the registry.
     * @param policyId Hash of the policy ID string
     * @param commitmentHash SHA-256 of the audit packet
     * @param status Initial policy status
     */
    function commitPolicy(
        bytes32 policyId,
        bytes32 commitmentHash,
        PolicyStatus status
    ) external returns (uint256 committedAt) {
        require(_records[policyId].committedAt == 0, "PolicyRegistry: policy already committed");

        _records[policyId] = PolicyRecord({
            policyId: policyId,
            commitmentHash: commitmentHash,
            status: status,
            committedAt: block.timestamp,
            committedBy: msg.sender
        });

        _allPolicyIds.push(policyId);

        emit PolicyCommitted(policyId, commitmentHash, status, block.timestamp, msg.sender);

        return block.timestamp;
    }

    /**
     * @notice Update the status of an existing policy.
     * @param policyId Hash of the policy ID string
     * @param newStatus New policy status
     */
    function updatePolicyStatus(
        bytes32 policyId,
        PolicyStatus newStatus
    ) external onlyPolicyExists(policyId) {
        _records[policyId].status = newStatus;

        emit PolicyStatusUpdated(policyId, newStatus, block.timestamp, msg.sender);
    }

    /**
     * @notice Get a policy record.
     * @param policyId Hash of the policy ID string
     * @return record The policy record
     */
    function getPolicy(bytes32 policyId) external view onlyPolicyExists(policyId) returns (PolicyRecord memory record) {
        return _records[policyId];
    }

    /**
     * @notice Check if a policy has been committed.
     * @param policyId Hash of the policy ID string
     * @return exists Whether the policy exists
     */
    function policyExists(bytes32 policyId) external view returns (bool exists) {
        return _records[policyId].committedAt > 0;
    }

    /**
     * @notice Get the total number of committed policies.
     * @return count Total number of policies
     */
    function getPolicyCount() external view returns (uint256 count) {
        return _allPolicyIds.length;
    }

    /**
     * @notice Get a policy by index.
     * @param index Index in the policy array
     * @return policyId Hash of the policy ID string
     */
    function getPolicyByIndex(uint256 index) external view onlyPolicyCountGte(index) returns (bytes32 policyId) {
        return _allPolicyIds[index];
    }

    /**
     * @notice Get the status of a policy.
     * @param policyId Hash of the policy ID string
     * @return status The policy status
     */
    function getPolicyStatus(bytes32 policyId) external view onlyPolicyExists(policyId) returns (PolicyStatus status) {
        return _records[policyId].status;
    }

    // -----------------------------------------------------------------------
    // View functions
    // -----------------------------------------------------------------------

    /**
     * @notice Get the commitment hash of a policy.
     * @param policyId Hash of the policy ID string
     * @return hash The commitment hash
     */
    function getCommitmentHash(bytes32 policyId) external view onlyPolicyExists(policyId) returns (bytes32 hash) {
        return _records[policyId].commitmentHash;
    }

    /**
     * @notice Get the committed timestamp of a policy.
     * @param policyId Hash of the policy ID string
     * @return timestamp The committed timestamp
     */
    function getCommittedAt(bytes32 policyId) external view onlyPolicyExists(policyId) returns (uint256 timestamp) {
        return _records[policyId].committedAt;
    }

    // -----------------------------------------------------------------------
    // Internal functions
    // -----------------------------------------------------------------------

    /**
     * @notice Modifier to ensure policy count is greater than index.
     * @param index Index to check
     */
    modifier onlyPolicyCountGte(uint256 index) {
        require(index < _allPolicyIds.length, "PolicyRegistry: index out of bounds");
        _;
    }
}
