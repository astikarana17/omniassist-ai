"""Unit tests for the customer-health scoring + gap-normalization pure logic."""
from __future__ import annotations

from app.models.enums import HealthCategory
from app.services.ops_service import (
    HEALTH_WEIGHTS,
    categorize,
    compute_health,
    normalize_question,
)


def test_weights_sum_to_one():
    assert round(sum(HEALTH_WEIGHTS.values()), 6) == 1.0


def test_perfect_account_is_healthy():
    r = compute_health(100, 100, 100, 100, 100)
    assert r["score"] == 100
    assert r["category"] == HealthCategory.HEALTHY.value
    assert r["churn_risk"] == 0.0


def test_zero_account_is_critical():
    r = compute_health(0, 0, 0, 0, 0)
    assert r["score"] == 0
    assert r["category"] == HealthCategory.CRITICAL.value
    assert r["churn_risk"] == 1.0


def test_category_thresholds():
    assert categorize(70) == HealthCategory.HEALTHY
    assert categorize(69) == HealthCategory.AT_RISK
    assert categorize(40) == HealthCategory.AT_RISK
    assert categorize(39) == HealthCategory.CRITICAL


def test_weighted_score_and_weakest_driver():
    # usage is weighted highest (0.30); make it the weakest dimension.
    r = compute_health(usage_score=10, engagement_score=90, support_score=90,
                       satisfaction_score=90, adoption_score=90)
    # 10*.3 + 90*.7 = 3 + 63 = 66
    assert r["score"] == 66
    assert r["category"] == HealthCategory.AT_RISK.value
    assert r["drivers"]["weakest"] == "usage_score"


def test_churn_risk_is_inverse_of_score():
    r = compute_health(60, 60, 60, 60, 60)
    assert r["score"] == 60
    assert r["churn_risk"] == 0.4


def test_normalize_question_clusters_duplicates():
    a = normalize_question("How do I reset my PASSWORD?")
    b = normalize_question("how do i reset my password")
    c = normalize_question("  How   do I   reset my password!!!  ")
    assert a == b == c == "how do i reset my password"


def test_normalize_distinct_questions_differ():
    assert normalize_question("reset password") != normalize_question("change email")
