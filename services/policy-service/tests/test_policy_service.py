"""Tests for the Policy Service."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from policy_service.domain.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    AuditEventType,
    AuditPacket,
    BindMethod,
    BindRequest,
    BindRequestInput,
    Coverage,
    PolicyDocumentType,
    PolicyHolder,
    PolicyLifecycle,
    PolicyResponse,
    PolicyState,
    PolicyStateTransition,
    PolicyTransitionError,
    VehicleInfo,
)
from policy_service.engine.policy_engine import PolicyEngine
from policy_service.storage.policy_store import PolicyStore


# ---------------------------------------------------------------------------
# Domain model tests
# ---------------------------------------------------------------------------


class TestPolicyStateTransition:
    def test_from_dict(self):
        data = {
            "from_state": "draft",
            "to_state": "pending_bind",
            "requires_approval": True,
            "description": "Submit draft for binding",
        }
        transition = PolicyStateTransition(**data)
        assert transition.from_state == PolicyState.DRAFT
        assert transition.to_state == PolicyState.PENDING_BIND
        assert transition.requires_approval is True


class TestPolicyLifecycle:
    def test_get_valid_transitions(self):
        lifecycle = PolicyLifecycle(
            states=[
                PolicyStateTransition(
                    from_state=PolicyState.DRAFT,
                    to_state=PolicyState.PENDING_BIND,
                ),
                PolicyStateTransition(
                    from_state=PolicyState.PENDING_BIND,
                    to_state=PolicyState.ACTIVE,
                ),
            ]
        )
        valid = lifecycle.get_valid_transitions(PolicyState.DRAFT)
        assert valid == [PolicyState.PENDING_BIND]

    def test_is_valid_transition(self):
        lifecycle = PolicyLifecycle(
            states=[
                PolicyStateTransition(
                    from_state=PolicyState.DRAFT,
                    to_state=PolicyState.PENDING_BIND,
                ),
            ]
        )
        assert lifecycle.is_valid_transition(PolicyState.DRAFT, PolicyState.PENDING_BIND) is True
        assert lifecycle.is_valid_transition(PolicyState.DRAFT, PolicyState.ACTIVE) is False


class TestAuditPacket:
    def test_to_dict(self):
        packet = AuditPacket(
            event_type=AuditEventType.BIND,
            policy_id=uuid4(),
            commitment_hash="abc123",
            metadata={"from_state": "draft"},
        )
        d = packet.to_dict()
        assert d["event_type"] == AuditEventType.BIND
        assert "policy_id" in d
        assert d["commitment_hash"] == "abc123"
        assert "created_at" in d

    def test_to_on_chain_record(self):
        packet = AuditPacket(
            event_type=AuditEventType.BIND,
            policy_id=uuid4(),
            commitment_hash="abc123",
        )
        record = packet.to_on_chain_record()
        assert "policy_id" in record
        assert record["commitment_hash"] == "abc123"
        assert record["status"] == AuditEventType.BIND
        assert "committed_at" in record


class TestBindRequest:
    def test_to_dict(self):
        holder = PolicyHolder(
            name="John Doe",
            address="123 Main St",
            phone="555-1234",
            email="john@example.com",
            driver_license="DL123",
            date_of_birth="1990-01-01",
        )
        vehicle = VehicleInfo(
            make="Toyota",
            model="Camry",
            year=2023,
            vin="1HGBH41JXMN109186",
            license_plate="ABC123",
            state="NC",
            mileage=15000,
            primary_use="commute",
            garage_location="123 Main St",
        )
        coverages = [
            Coverage(type="liability", limit=50000, deductible=500, premium=500.0),
        ]
        request = BindRequest(
            quote_id=uuid4(),
            policy_id=uuid4(),
            policy_holder=holder,
            vehicle=vehicle,
            coverages=coverages,
            total_premium=1100.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
            bind_method=BindMethod.HUMAN_APPROVAL,
        )
        d = request.to_dict()
        assert d["policy_holder"]["name"] == "John Doe"
        assert d["vehicle"]["make"] == "Toyota"
        assert d["total_premium"] == 1100.0


class TestApprovalRequest:
    def test_to_dict(self):
        bind_request = BindRequest(
            quote_id=uuid4(),
            policy_id=uuid4(),
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
            bind_method=BindMethod.HUMAN_APPROVAL,
        )
        approval = ApprovalRequest(
            bind_request=bind_request,
            approval_status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        d = approval.to_dict()
        assert d["approval_status"] == ApprovalStatus.PENDING
        assert "expires_at" in d


# ---------------------------------------------------------------------------
# Engine tests
# ---------------------------------------------------------------------------


class TestPolicyEngine:
    def test_default_lifecycle(self):
        engine = PolicyEngine()
        valid = engine.get_valid_transitions(PolicyState.DRAFT)
        assert PolicyState.PENDING_BIND in valid

    def test_generate_audit_packet(self):
        engine = PolicyEngine()
        policy_id = uuid4()
        packet = engine.generate_audit_packet(AuditEventType.BIND, policy_id)

        assert packet.event_type == AuditEventType.BIND
        assert packet.policy_id == policy_id
        assert packet.commitment_hash
        assert len(packet.metadata) == 0

    def test_create_bind_request(self):
        engine = PolicyEngine()
        input_data = BindRequestInput(
            quote_id=uuid4(),
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        quote_data = {
            "policy_holder_name": "John Doe",
            "policy_holder_address": "123 Main St",
            "policy_holder_phone": "555-1234",
            "policy_holder_email": "john@example.com",
            "driver_license": "DL123",
            "date_of_birth": "1990-01-01",
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_year": 2023,
            "vehicle_vin": "1HGBH41JXMN109186",
            "license_plate": "ABC123",
            "vehicle_state": "NC",
            "vehicle_mileage": 15000,
            "vehicle_primary_use": "commute",
            "garage_location": "123 Main St",
            "coverages": [
                {"type": "liability", "limit": 50000, "deductible": 500, "premium": 500.0},
            ],
            "total_premium": 1100.0,
        }
        bind_request = engine.create_bind_request(input_data, quote_data)

        assert bind_request.policy_id
        assert bind_request.policy_holder.name == "John Doe"
        assert bind_request.vehicle.make == "Toyota"
        assert bind_request.total_premium == 1100.0

    def test_create_approval_request(self):
        engine = PolicyEngine()
        bind_request = BindRequest(
            quote_id=uuid4(),
            policy_id=uuid4(),
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
            bind_method=BindMethod.HUMAN_APPROVAL,
        )
        approval_request = engine.create_approval_request(bind_request, expires_in_hours=24)

        assert approval_request.approval_status == ApprovalStatus.PENDING
        assert approval_request.expires_at > datetime.utcnow()

    def test_process_approval_approved(self):
        engine = PolicyEngine()
        bind_request = BindRequest(
            quote_id=uuid4(),
            policy_id=uuid4(),
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
            bind_method=BindMethod.HUMAN_APPROVAL,
        )
        approval_request = ApprovalRequest(bind_request=bind_request)
        decision = ApprovalDecision(
            approval_status=ApprovalStatus.APPROVED,
            approver="underwriter_1",
            comments="All checks passed",
        )
        result = engine.process_approval(approval_request, decision)

        assert result["success"] is True
        assert approval_request.approval_status == ApprovalStatus.APPROVED
        assert approval_request.approver == "underwriter_1"

    def test_process_approval_rejected(self):
        engine = PolicyEngine()
        bind_request = BindRequest(
            quote_id=uuid4(),
            policy_id=uuid4(),
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
            bind_method=BindMethod.HUMAN_APPROVAL,
        )
        approval_request = ApprovalRequest(bind_request=bind_request)
        decision = ApprovalDecision(
            approval_status=ApprovalStatus.REJECTED,
            approver="underwriter_1",
            comments="High risk driver",
        )
        result = engine.process_approval(approval_request, decision)

        assert result["success"] is False
        assert approval_request.approval_status == ApprovalStatus.REJECTED

    def test_transition_valid(self):
        engine = PolicyEngine()
        policy_id = uuid4()
        result = engine.transition_state(PolicyState.DRAFT, PolicyState.PENDING_BIND, policy_id)

        assert result["success"] is True
        assert result["new_state"] == PolicyState.PENDING_BIND

    def test_transition_invalid(self):
        engine = PolicyEngine()
        policy_id = uuid4()
        with pytest.raises(PolicyTransitionError):
            engine.transition_state(PolicyState.DRAFT, PolicyState.ACTIVE, policy_id)

    def test_transition_to_active_generates_audit_packet(self):
        engine = PolicyEngine()
        policy_id = uuid4()
        result = engine.transition_state(PolicyState.PENDING_BIND, PolicyState.ACTIVE, policy_id)

        assert result["audit_packet"] is not None
        assert result["audit_packet"].event_type == AuditEventType.BIND

    def test_generate_policy_document(self):
        engine = PolicyEngine()
        policy_id = uuid4()
        doc = engine.generate_policy_document(
            policy_id,
            PolicyDocumentType.POLICY_DECLARATION,
            "Policy declaration content",
            {"version": "1.0"},
        )
        assert doc["type"] == PolicyDocumentType.POLICY_DECLARATION
        assert doc["content"] == "Policy declaration content"
        assert "created_at" in doc


# ---------------------------------------------------------------------------
# Storage tests
# ---------------------------------------------------------------------------


class TestPolicyStore:
    def setup_method(self):
        self.store = PolicyStore()

    def test_create_policy(self):
        policy_id = uuid4()
        policy = self.store.create_policy(
            policy_id=policy_id,
            state=PolicyState.ACTIVE,
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[Coverage(type="liability", limit=50000, deductible=500, premium=500.0)],
            total_premium=1100.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        assert policy["policy_id"] == str(policy_id)
        assert policy["state"] == PolicyState.ACTIVE
        assert policy["total_premium"] == 1100.0

    def test_get_policy(self):
        policy_id = uuid4()
        self.store.create_policy(
            policy_id=policy_id,
            state=PolicyState.ACTIVE,
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        policy = self.store.get_policy(policy_id)
        assert policy is not None
        assert policy["policy_id"] == str(policy_id)

    def test_get_policy_not_found(self):
        policy = self.store.get_policy(uuid4())
        assert policy is None

    def test_update_policy_state(self):
        policy_id = uuid4()
        self.store.create_policy(
            policy_id=policy_id,
            state=PolicyState.DRAFT,
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        updated = self.store.update_policy_state(policy_id, PolicyState.ACTIVE)
        assert updated["state"] == PolicyState.ACTIVE
        assert updated["bind_date"] is not None

    def test_add_audit_packet(self):
        policy_id = uuid4()
        packet = AuditPacket(
            event_type=AuditEventType.BIND,
            policy_id=policy_id,
            commitment_hash="abc123",
        )
        self.store.add_audit_packet(policy_id, packet)
        packets = self.store.get_audit_packets(policy_id)
        assert len(packets) == 1
        assert packets[0].event_type == AuditEventType.BIND

    def test_list_policies(self):
        policy_id1 = uuid4()
        policy_id2 = uuid4()
        self.store.create_policy(
            policy_id=policy_id1,
            state=PolicyState.ACTIVE,
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        self.store.create_policy(
            policy_id=policy_id2,
            state=PolicyState.DRAFT,
            policy_holder=PolicyHolder(
                name="Jane Doe",
                address="456 Oak St",
                phone="555-5678",
                email="jane@example.com",
                driver_license="DL456",
                date_of_birth="1995-06-15",
            ),
            vehicle=VehicleInfo(
                make="Honda",
                model="Civic",
                year=2022,
                vin="2HGFC2F59MH123456",
                license_plate="DEF456",
                state="NC",
                mileage=20000,
                primary_use="commute",
                garage_location="456 Oak St",
            ),
            coverages=[],
            total_premium=900.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        policies = self.store.list_policies()
        assert len(policies) == 2

    def test_list_policies_filtered(self):
        policy_id1 = uuid4()
        policy_id2 = uuid4()
        self.store.create_policy(
            policy_id=policy_id1,
            state=PolicyState.ACTIVE,
            policy_holder=PolicyHolder(
                name="John Doe",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com",
                driver_license="DL123",
                date_of_birth="1990-01-01",
            ),
            vehicle=VehicleInfo(
                make="Toyota",
                model="Camry",
                year=2023,
                vin="1HGBH41JXMN109186",
                license_plate="ABC123",
                state="NC",
                mileage=15000,
                primary_use="commute",
                garage_location="123 Main St",
            ),
            coverages=[],
            total_premium=1000.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        self.store.create_policy(
            policy_id=policy_id2,
            state=PolicyState.DRAFT,
            policy_holder=PolicyHolder(
                name="Jane Doe",
                address="456 Oak St",
                phone="555-5678",
                email="jane@example.com",
                driver_license="DL456",
                date_of_birth="1995-06-15",
            ),
            vehicle=VehicleInfo(
                make="Honda",
                model="Civic",
                year=2022,
                vin="2HGFC2F59MH123456",
                license_plate="DEF456",
                state="NC",
                mileage=20000,
                primary_use="commute",
                garage_location="456 Oak St",
            ),
            coverages=[],
            total_premium=900.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        active_policies = self.store.list_policies(state=PolicyState.ACTIVE)
        assert len(active_policies) == 1
        assert active_policies[0]["policy_id"] == str(policy_id1)

    def test_get_documents(self):
        policy_id = uuid4()
        self.store.add_document(
            policy_id,
            PolicyDocumentType.POLICY_DECLARATION,
            "Policy declaration content",
        )
        docs = self.store.get_documents(policy_id)
        assert len(docs) == 1
        assert docs[0]["type"] == PolicyDocumentType.POLICY_DECLARATION

    def test_add_document(self):
        policy_id = uuid4()
        doc = self.store.add_document(
            policy_id,
            PolicyDocumentType.POLICY_DECLARATION,
            "Policy declaration content",
            {"version": "1.0"},
        )
        assert doc["type"] == PolicyDocumentType.POLICY_DECLARATION
        assert doc["content"] == "Policy declaration content"
        docs = self.store.get_documents(policy_id)
        assert len(docs) == 1
