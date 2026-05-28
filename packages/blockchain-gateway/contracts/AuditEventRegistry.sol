// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title AuditEventRegistry
 * @notice Immutable audit event log for insurance operations.
 *         Only stores event_type, policy_id, commitment_hash, committed_at.
 *         Customer data is NEVER stored on-chain.
 */
contract AuditEventRegistry {
    enum EventType {
        BIND,
        ENDORSEMENT,
        CANCELLATION,
        RENEWAL,
        CLAIM_FILING,
        CLAIM_SETTLEMENT
    }

    struct AuditEvent {
        bytes32 eventType;      // Hash of event type string
        bytes32 policyId;       // Hash of policy ID string
        bytes32 commitmentHash; // SHA-256 of audit packet
        uint256 committedAt;    // Timestamp of commitment
        address committedBy;    // Address that committed
    }

    // Array of all audit events (append-only)
    AuditEvent[] private _events;

    // Mapping from event hash to index (for lookup)
    mapping(bytes32 => uint256) private _eventIndices;

    // Events
    event AuditEventRecorded(
        bytes32 indexed eventType,
        bytes32 indexed policyId,
        bytes32 commitmentHash,
        uint256 committedAt,
        address committedBy
    );

    // -----------------------------------------------------------------------
    // Public functions
    // -----------------------------------------------------------------------

    /**
     * @notice Record an audit event.
     * @param eventTypeHash Hash of the event type string
     * @param policyIdHash Hash of the policy ID string
     * @param commitmentHash SHA-256 of the audit packet
     * @return eventIndex Index of the recorded event
     */
    function recordEvent(
        bytes32 eventTypeHash,
        bytes32 policyIdHash,
        bytes32 commitmentHash
    ) external returns (uint256 eventIndex) {
        uint256 index = _events.length;

        _events.push(AuditEvent({
            eventType: eventTypeHash,
            policyId: policyIdHash,
            commitmentHash: commitmentHash,
            committedAt: block.timestamp,
            committedBy: msg.sender
        }));

        _eventIndices[keccak256(abi.encodePacked(eventTypeHash, policyIdHash, commitmentHash, block.timestamp))] = index;

        emit AuditEventRecorded(eventTypeHash, policyIdHash, commitmentHash, block.timestamp, msg.sender);

        return index;
    }

    /**
     * @notice Get an audit event by index.
     * @param index Index of the event
     * @return evt The audit event
     */
    function getEvent(uint256 index) external view returns (AuditEvent memory evt) {
        require(index < _events.length, "AuditEventRegistry: index out of bounds");
        return _events[index];
    }

    /**
     * @notice Get the total number of audit events.
     * @return count Total number of events
     */
    function getEventCount() external view returns (uint256 count) {
        return _events.length;
    }

    /**
     * @notice Get audit events for a policy.
     * @param policyIdHash Hash of the policy ID string
     * @return eventIndices Array of event indices for the policy
     */
    function getPolicyEvents(bytes32 policyIdHash) external view returns (uint256[] memory eventIndices) {
        // In production, use a mapping from policyId => event indices
        // For MVP, iterate all events (inefficient but simple)
        uint256[] memory temp = new uint256[](_events.length);
        uint256 count = 0;

        for (uint256 i = 0; i < _events.length; i++) {
            if (_events[i].policyId == policyIdHash) {
                temp[count] = i;
                count++;
            }
        }

        // Resize array
        eventIndices = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            eventIndices[i] = temp[i];
        }
    }

    /**
     * @notice Get audit events by event type.
     * @param eventTypeHash Hash of the event type string
     * @return eventIndices Array of event indices for the event type
     */
    function getEventsByType(bytes32 eventTypeHash) external view returns (uint256[] memory eventIndices) {
        uint256[] memory temp = new uint256[](_events.length);
        uint256 count = 0;

        for (uint256 i = 0; i < _events.length; i++) {
            if (_events[i].eventType == eventTypeHash) {
                temp[count] = i;
                count++;
            }
        }

        eventIndices = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            eventIndices[i] = temp[i];
        }
    }
}
