"""
Admin Dashboard API Routes
Provides endpoints for viewing system data, metrics, and analytics
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import os

router = APIRouter()

# Path to demo data
DEMO_DATA_DIR = Path(__file__).parent.parent.parent / "demo_data"


def load_csv_data(filename: str) -> List[Dict[str, Any]]:
    """Load CSV data and return as list of dictionaries"""
    try:
        file_path = DEMO_DATA_DIR / filename
        if not file_path.exists():
            return []
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading {filename}: {str(e)}")


@router.get("/overview")
async def get_dashboard_overview():
    """Get overall system statistics and overview"""
    try:
        # Load all data
        cases = load_csv_data("sample_patient_cases.csv")
        diagnoses = load_csv_data("diagnoses_data.csv")
        metrics = load_csv_data("system_metrics.csv")

        # Calculate statistics
        total_cases = len(cases)
        total_diagnoses = len(diagnoses)

        # Count by review tier
        tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0, "tier4": 0}
        for case in cases:
            tier = f"tier{case['review_tier']}"
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Average confidence from diagnoses
        if diagnoses:
            avg_confidence = sum(d['confidence_score'] for d in diagnoses) / len(diagnoses)
        else:
            avg_confidence = 0.0

        # Recent metrics
        if metrics:
            latest_metrics = metrics[-1]
            avg_response_time = latest_metrics['avg_response_time_ms']
            cache_hit_rate = latest_metrics['cache_hit_rate']
            uptime = latest_metrics['uptime_percentage']
        else:
            avg_response_time = 0
            cache_hit_rate = 0
            uptime = 0

        # Count red flags
        red_flag_count = sum(1 for d in diagnoses if d.get('red_flags', ''))

        # Top conditions
        condition_counts = {}
        for dx in diagnoses:
            condition = dx['condition_name']
            condition_counts[condition] = condition_counts.get(condition, 0) + 1

        top_conditions = sorted(
            condition_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_cases": total_cases,
            "total_diagnoses": total_diagnoses,
            "average_confidence": round(avg_confidence, 3),
            "tier_distribution": tier_counts,
            "red_flags_detected": red_flag_count,
            "performance_metrics": {
                "avg_response_time_ms": avg_response_time,
                "cache_hit_rate": round(cache_hit_rate, 3),
                "uptime_percentage": uptime
            },
            "top_conditions": [{"name": name, "count": count} for name, count in top_conditions],
            "status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases")
async def get_all_cases(limit: int = 50, offset: int = 0):
    """Get all patient cases with pagination"""
    try:
        cases = load_csv_data("sample_patient_cases.csv")
        total = len(cases)

        # Apply pagination
        paginated_cases = cases[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "cases": paginated_cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}")
async def get_case_details(case_id: str):
    """Get detailed information for a specific case"""
    try:
        cases = load_csv_data("sample_patient_cases.csv")
        diagnoses = load_csv_data("diagnoses_data.csv")

        # Find the case
        case = next((c for c in cases if c['case_id'] == case_id), None)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        # Find associated diagnoses
        case_diagnoses = [d for d in diagnoses if d['case_id'] == case_id]

        # Sort by rank
        case_diagnoses.sort(key=lambda x: x['differential_rank'])

        return {
            "case": case,
            "diagnoses": case_diagnoses,
            "diagnosis_count": len(case_diagnoses)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnoses")
async def get_all_diagnoses(limit: int = 100, offset: int = 0):
    """Get all diagnoses with pagination"""
    try:
        diagnoses = load_csv_data("diagnoses_data.csv")
        total = len(diagnoses)

        # Apply pagination
        paginated_diagnoses = diagnoses[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "diagnoses": paginated_diagnoses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_system_metrics(days: int = 14):
    """Get system performance metrics"""
    try:
        metrics = load_csv_data("system_metrics.csv")

        # Get recent metrics
        recent_metrics = metrics[-days:] if len(metrics) > days else metrics

        # Calculate aggregated statistics
        if recent_metrics:
            total_cases = sum(m['total_cases_analyzed'] for m in recent_metrics)
            avg_confidence = sum(m['avg_confidence_score'] for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m['avg_response_time_ms'] for m in recent_metrics) / len(recent_metrics)
            avg_cache_hit_rate = sum(m['cache_hit_rate'] for m in recent_metrics) / len(recent_metrics)
            avg_uptime = sum(m['uptime_percentage'] for m in recent_metrics) / len(recent_metrics)
            total_red_flags = sum(m['red_flags_detected'] for m in recent_metrics)
            total_rare_diseases = sum(m['rare_diseases_identified'] for m in recent_metrics)
        else:
            total_cases = avg_confidence = avg_response_time = 0
            avg_cache_hit_rate = avg_uptime = total_red_flags = total_rare_diseases = 0

        return {
            "period_days": days,
            "metrics_data": recent_metrics,
            "aggregated_stats": {
                "total_cases_analyzed": total_cases,
                "average_confidence_score": round(avg_confidence, 3),
                "average_response_time_ms": round(avg_response_time, 2),
                "average_cache_hit_rate": round(avg_cache_hit_rate, 3),
                "average_uptime_percentage": round(avg_uptime, 2),
                "total_red_flags_detected": total_red_flags,
                "total_rare_diseases_identified": total_rare_diseases
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/conditions")
async def get_condition_analytics():
    """Get analytics on diagnosed conditions"""
    try:
        diagnoses = load_csv_data("diagnoses_data.csv")

        # Count by condition
        condition_stats = {}
        for dx in diagnoses:
            condition = dx['condition_name']
            if condition not in condition_stats:
                condition_stats[condition] = {
                    "name": condition,
                    "count": 0,
                    "avg_confidence": 0,
                    "total_confidence": 0,
                    "icd10_code": dx['icd10_code']
                }
            condition_stats[condition]["count"] += 1
            condition_stats[condition]["total_confidence"] += dx['confidence_score']

        # Calculate averages
        for condition in condition_stats.values():
            condition["avg_confidence"] = round(
                condition["total_confidence"] / condition["count"], 3
            )
            del condition["total_confidence"]

        # Sort by count
        sorted_conditions = sorted(
            condition_stats.values(),
            key=lambda x: x['count'],
            reverse=True
        )

        return {
            "total_unique_conditions": len(sorted_conditions),
            "conditions": sorted_conditions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/specialists")
async def get_specialist_analytics():
    """Get analytics on recommended specialists"""
    try:
        diagnoses = load_csv_data("diagnoses_data.csv")

        # Count specialist recommendations
        specialist_counts = {}
        for dx in diagnoses:
            specialists = dx.get('recommended_specialists', '').split(', ')
            for specialist in specialists:
                specialist = specialist.strip()
                if specialist:
                    specialist_counts[specialist] = specialist_counts.get(specialist, 0) + 1

        # Sort by count
        sorted_specialists = sorted(
            [{"name": name, "count": count} for name, count in specialist_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )

        return {
            "total_unique_specialists": len(sorted_specialists),
            "specialists": sorted_specialists
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/timeline")
async def get_timeline_analytics():
    """Get case analytics over time"""
    try:
        cases = load_csv_data("sample_patient_cases.csv")

        # Group by date
        timeline_data = {}
        for case in cases:
            date = case['created_at'][:10]  # Extract date part
            if date not in timeline_data:
                timeline_data[date] = {
                    "date": date,
                    "total_cases": 0,
                    "tier1": 0,
                    "tier2": 0,
                    "tier3": 0,
                    "tier4": 0
                }
            timeline_data[date]["total_cases"] += 1
            tier = f"tier{case['review_tier']}"
            timeline_data[date][tier] += 1

        # Sort by date
        sorted_timeline = sorted(timeline_data.values(), key=lambda x: x['date'])

        return {
            "timeline": sorted_timeline,
            "total_days": len(sorted_timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/demographics")
async def get_demographic_analytics():
    """Get demographic analytics of patients"""
    try:
        cases = load_csv_data("sample_patient_cases.csv")

        # Age groups
        age_groups = {
            "0-17": 0,
            "18-30": 0,
            "31-50": 0,
            "51-70": 0,
            "71+": 0
        }

        # Gender distribution
        gender_distribution = {"M": 0, "F": 0, "Other": 0}

        for case in cases:
            age = case['patient_age']
            if age <= 17:
                age_groups["0-17"] += 1
            elif age <= 30:
                age_groups["18-30"] += 1
            elif age <= 50:
                age_groups["31-50"] += 1
            elif age <= 70:
                age_groups["51-70"] += 1
            else:
                age_groups["71+"] += 1

            sex = case['patient_sex']
            if sex in gender_distribution:
                gender_distribution[sex] += 1
            else:
                gender_distribution["Other"] += 1

        return {
            "age_distribution": [
                {"group": group, "count": count}
                for group, count in age_groups.items()
            ],
            "gender_distribution": [
                {"gender": gender, "count": count}
                for gender, count in gender_distribution.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def dashboard_health():
    """Health check endpoint for dashboard"""
    return {
        "status": "healthy",
        "service": "Dashboard API",
        "timestamp": datetime.utcnow().isoformat(),
        "data_available": {
            "cases": os.path.exists(DEMO_DATA_DIR / "sample_patient_cases.csv"),
            "diagnoses": os.path.exists(DEMO_DATA_DIR / "diagnoses_data.csv"),
            "metrics": os.path.exists(DEMO_DATA_DIR / "system_metrics.csv")
        }
    }
