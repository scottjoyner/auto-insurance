/**
 * Claims Service - Fraud Detection Utility (Phase P1.5)
 * 
   Provides basic fraud detection rules and risk scoring for claim payments
 */

export interface FraudCheckResult {
  is_suspect: boolean;
  risk_score: number; // 0.0 - 1.0 (lower is safer)
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  reasons: Array<string>;
  recommendation: 'approve' | 'review' | 'reject';
}

/**
 * Basic Fraud Detection Rules Engine
 * 
   Implements simple fraud detection rules for claim payments.
   Real production implementation would integrate with external providers like:
   - Experian IdentityWorks
   - LexisNexis Risk Solutions
   - First Advantage Fraud Watch
 */
export class FraudDetectionEngine {
  /**
   * Check claim payment for fraud indicators
   * @param claimData Claim data to check
   * @returns Fraud assessment with risk score and recommendations
   */
  async checkPaymentForFraud(claimData: any): Promise<FraudCheckResult> {
    const reasons: Array<string> = [];
    let riskScore = 0; // Start with low risk

    // Rule 1: Check claim amount patterns (sudden large claims are suspicious)
    if (claimData.claim_amount && claimData.claim_amount > 10000) {
      reasons.push(`Large claim amount ($${claimData.claim_amount.toLocaleString()}) flagged for review`);
      riskScore += 0.3; // +30% risk
    }

    // Rule 2: Check if policy is active and current period
    if (!claimData.is_policy_active) {
      reasons.push('Policy is not currently active - fraud indicator');
      riskScore += 0.5; // +50% risk
    }

    // Rule 3: Verify claim type matches covered perils
    if (!claimData.claim_type_is_covered_peril) {
      reasons.push('Claim type may not be covered under policy - potential fraud');
      riskScore += 0.4; // +40% risk
    }

    // Rule 4: Check for identity theft indicators
    if (claimData.identity_verification_failed) {
      reasons.push('Identity verification failed - fraud indicator');
      riskScore += 0.6; // +60% risk
    }

    // Rule 5: Verify incident date is reasonable (not future-dated)
    const today = new Date();
    const incidentDate = new Date(claimData.incident_date);
    if (incidentDate > today) {
      reasons.push('Incident date is in the future - potential fraud');
      riskScore += 0.5; // +50% risk
    }

    // Rule 6: Check for duplicate claims on same incident
    if (claimData.duplicate_claim_detected) {
      reasons.push('Duplicate claim detected for same incident - fraud indicator');
      riskScore += 0.7; // +70% risk
    }

    // Rule 7: Verify payment method matches customer preference
    if (!claimData.payment_method_matches_customer_preference) {
      reasons.push('Payment method differs from customer preference - potential red flag');
      riskScore += 0.15; // +15% risk
    }

    // Cap risk score at maximum threshold
    riskScore = Math.min(riskScore, 1.0);

    // Determine risk level and recommendation
    const riskLevel: 'low' | 'medium' | 'high' | 'critical' = this.getRiskLevel(riskScore);
    const recommendation = this.getRecommendation(riskScore);

    console.log(`[FRAUD_DETECTION_ENGINE] Assessment for claim ${claimData.claim_id}: risk=${riskScore}, level=${riskLevel}, recommendation=${recommendation}`);

    return {
      is_suspect: riskScore >= 0.3, // Flag as suspect if risk score is medium or higher
      risk_score: riskScore,
      risk_level: riskLevel,
      reasons,
      recommendation
    };
  }

  /**
   * Verify claim payment details against fraud patterns
   */
  async verifyPaymentDetails(paymentsData: any): Promise<FraudCheckResult> {
    const reasons: Array<string> = [];
    let riskScore = 0;

    // Rule: Check for unusual payment timing
    const today = new Date();
    if (paymentsData.payment_initiated_time && this.isUnusualTime(paymentsData.payment_initiated_time)) {
      reasons.push('Payment initiated during unusual time - potential red flag');
      riskScore += 0.1;
    }

    // Rule: Check for mismatched amounts in split payments
    if (paymentsData.split_payments && paymentsData.split_payments.length > 0) {
      const totalSplit = paymentsData.split_payments.reduce((sum: number, p: any) => sum + p.amount, 0);
      const claimedAmount = paymentsData.claim_amount;

      if (Math.abs(totalSplit - claimedAmount) > 0.01) {
        reasons.push('Split payment total does not match claimed amount');
        riskScore += 0.2;
      }
    }

    // Rule: Check for external fraud watch alerts
    if (paymentsData.external_fraud_alert) {
      reasons.push('External fraud watch alert triggered - immediate review required');
      riskScore += 0.8;
    }

    const riskLevel = this.getRiskLevel(riskScore);
    const recommendation = this.getRecommendation(riskScore);

    return {
      is_suspect: riskScore >= 0.3,
      risk_score: riskScore,
      risk_level: riskLevel,
      reasons,
      recommendation
    };
  }

  /**
   * Get risk level from score
   */
  private getRiskLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
    if (score < 0.2) return 'low';
    if (score < 0.5) return 'medium';
    if (score < 0.8) return 'high';
    return 'critical';
  }

  /**
   * Get recommendation based on risk score
   */
  private getRecommendation(score: number): 'approve' | 'review' | 'reject' {
    if (score < 0.2) return 'approve'; // Auto-approve low risk (< 20%)
    if (score < 0.5) return 'approve'; // Can auto-approve medium risk (< 50%)
    if (score < 0.8) return 'review'; // Manual review required for high risk
    return 'reject'; // Reject critical risk (>= 80%)
  }

  /**
   * Check if time is unusual (outside normal business hours)
   */
  private isUnusualTime(timestamp: string): boolean {
    const date = new Date(timestamp);
    const hour = date.getHours();
    const day = date.getDay(); // 0-6, where 6 is Saturday

    // Weekends are unusual
    if (day === 0 || day === 6) return true;

    // Night hours are unusual for payments
    return hour < 9 || hour > 17; // Outside 9 AM - 5 PM
  }

  /**
   * Add external fraud check result to assessment
   */
  async integrateExternalFraudCheck(externalResult: any): Promise<FraudCheckResult> {
    const reasons: Array<string> = [];
    let riskScore = this.calculateBaseRiskScore(); // Start with current base score

    // If external provider flagged as fraud, increase risk significantly
    if (externalResult.fraud_score && externalResult.fraud_score > 0.7) {
      reasons.push(`External fraud provider flagged: ${externalResult.provider_name} detected high fraud probability`);
      riskScore += (externalResult.fraud_score - 0.3) * 2; // Amplify external signal
    }

    // Check for specific external alerts
    if (externalResult.alerts && externalResult.alerts.length > 0) {
      reasons.push(`External alerts: ${externalResult.alerts.join(', ')}`);
      riskScore += 0.4;
    }

    const riskLevel = this.getRiskLevel(riskScore);
    const recommendation = this.getRecommendation(riskScore);

    return {
      is_suspect: riskScore >= 0.3,
      risk_score: Math.min(riskScore, 1.0), // Cap at 100%
      risk_level: riskLevel,
      reasons,
      recommendation
    };
  }

  /**
   * Calculate base risk score from previous checks
   */
  private calculateBaseRiskScore(): number {
    // In production, this would retrieve current risk score from database
    return 0.1; // Default low risk if no prior data
  }

  /**
   * Get fraud detection rules list for documentation
   */
  getFraudDetectionRules(): Array<{ rule: string; condition: string; weight: number }> {
    return [
      {
        rule: 'Large claim amount',
        condition: 'Claim amount exceeds $10,000',
        weight: 0.3
      },
      {
        rule: 'Inactive policy',
        condition: 'Policy is not active or expired',
        weight: 0.5
      },
      {
        rule: 'Uncovered peril',
        condition: 'Claim type not covered under policy',
        weight: 0.4
      },
      {
        rule: 'Identity verification failure',
        condition: 'Customer identity cannot be verified',
        weight: 0.6
      },
      {
        rule: 'Future-dated incident',
        condition: 'Incident date is in the future',
        weight: 0.5
      },
      {
        rule: 'Duplicate claim detection',
        condition: 'Claim matches existing incident',
        weight: 0.7
      },
      {
        rule: 'Mismatched payment method',
        condition: 'Payment method differs from customer preference',
        weight: 0.15
      },
      {
        rule: 'Unusual payment timing',
        condition: 'Payment made outside business hours',
        weight: 0.1
      },
      {
        rule: 'Split payment mismatch',
        condition: 'Split payment total does not match claim amount',
        weight: 0.2
      }
    ];
  }

  /**
   * Generate fraud assessment report for manual review
   */
  generateFraudReport(assessment: FraudCheckResult): Record<string, any> {
    return {
      report_id: `fraud-${Date.now()}`,
      generated_at: new Date().toISOString(),
      claim_summary: {
        is_suspect: assessment.is_suspect,
        risk_score: assessment.risk_score,
        risk_level: assessment.risk_level,
        recommendation: assessment.recommendation
      },
      risk_factors: assessment.reasons.map((reason, index) => ({
        factor: index + 1,
        description: reason
      })),
      action_required: assessment.recommendation === 'review' ? 'Manual underwriter review required' : null,
      next_steps: [
        assessment.recommendation === 'reject'
          ? 'Reject claim payment and notify customer of rejection reasons'
          : assessment.recommendation === 'review'
            ? 'Forward to underwriter team for manual fraud analysis'
            : 'Proceed with automated approval and payment processing'
      ]
    };
  }
}

// Export singleton instance for use across application
const fraudDetectionEngine = new FraudDetectionEngine();

export default fraudDetectionEngine;
export { FraudDetectionEngine, type FraudCheckResult };
