"""
Test script to verify the API is working correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import asyncio
from pprint import pprint

API_BASE_URL = "http://localhost:8000/api/v1"


async def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        pprint(response.json())


async def test_stats():
    """Test stats endpoint"""
    print("\n=== Testing Stats ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/stats")
        print(f"Status: {response.status_code}")
        pprint(response.json())


async def test_diagnostic_analysis():
    """Test diagnostic analysis endpoint"""
    print("\n=== Testing Diagnostic Analysis ===")

    # Sample patient case
    patient_case = {
        "case_id": "test_case_001",
        "age": 35,
        "sex": "female",
        "chief_complaint": "I've been feeling extremely tired and have gained weight despite not eating more",
        "symptoms": [
            {
                "description": "Persistent fatigue and weakness",
                "severity": "moderate",
                "duration_days": 60,
                "frequency": "constant"
            },
            {
                "description": "Unexplained weight gain of 15 pounds",
                "severity": "moderate",
                "duration_days": 90,
                "frequency": "progressive"
            },
            {
                "description": "Always feeling cold, even in warm weather",
                "severity": "moderate",
                "duration_days": 60,
                "frequency": "constant"
            },
            {
                "description": "Dry skin and hair loss",
                "severity": "mild",
                "duration_days": 45,
                "frequency": "constant"
            },
            {
                "description": "Difficulty concentrating and mild depression",
                "severity": "moderate",
                "duration_days": 50,
                "frequency": "intermittent"
            }
        ],
        "medical_history": [],
        "family_history": ["thyroid disease in mother"],
        "current_medications": []
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/analyze",
            json=patient_case
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n=== Diagnostic Result ===")
            print(f"Case ID: {result['case_id']}")
            print(f"Overall Confidence: {result['overall_confidence']:.2%}")
            print(f"Review Tier: {result['review_tier']}")
            print(f"Emergency Care Required: {result['requires_emergency_care']}")
            print(f"Processing Time: {result['processing_time_ms']:.2f}ms")

            print(f"\n=== Differential Diagnoses ===")
            for i, diagnosis in enumerate(result['differential_diagnoses'][:5], 1):
                print(f"\n{i}. {diagnosis['condition_name']}")
                print(f"   Confidence: {diagnosis['confidence_score']:.2%}")
                print(f"   Similarity: {diagnosis['similarity_score']:.2%}")
                print(f"   Probability: {diagnosis['probability']:.2%}")
                print(f"   Matching Symptoms: {', '.join(diagnosis['matching_symptoms'][:3])}")
                print(f"   Recommended Tests: {', '.join(diagnosis['recommended_next_steps'][:3])}")

            print(f"\n=== Clinical Reasoning ===")
            print(result['reasoning_summary'])

            if result['recommended_specialists']:
                print(f"\n=== Recommended Specialists ===")
                print(", ".join(result['recommended_specialists']))

        else:
            print(f"Error: {response.text}")


async def test_rare_disease_case():
    """Test with a rare disease case"""
    print("\n\n=== Testing Rare Disease Case ===")

    # Case suggestive of Myotonic Dystrophy
    patient_case = {
        "case_id": "test_case_002",
        "age": 28,
        "sex": "male",
        "chief_complaint": "Progressive muscle weakness and difficulty releasing my grip",
        "symptoms": [
            {
                "description": "Progressive muscle weakness especially in hands and feet",
                "severity": "moderate",
                "duration_days": 730,  # 2 years
                "frequency": "progressive"
            },
            {
                "description": "Difficulty releasing grip after shaking hands (myotonia)",
                "severity": "moderate",
                "duration_days": 365,
                "frequency": "constant"
            },
            {
                "description": "Cataracts noticed during eye exam",
                "severity": "mild",
                "duration_days": 180,
                "frequency": "constant"
            },
            {
                "description": "Irregular heartbeat on ECG",
                "severity": "moderate",
                "duration_days": 90,
                "frequency": "intermittent"
            },
            {
                "description": "Excessive daytime sleepiness",
                "severity": "moderate",
                "duration_days": 365,
                "frequency": "constant"
            }
        ],
        "medical_history": [],
        "family_history": ["muscle disease in grandfather"],
        "current_medications": []
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/analyze",
            json=patient_case
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nOverall Confidence: {result['overall_confidence']:.2%}")
            print(f"Review Tier: {result['review_tier']}")

            print(f"\n=== Top Diagnoses ===")
            for i, diagnosis in enumerate(result['differential_diagnoses'][:3], 1):
                print(f"{i}. {diagnosis['condition_name']} - {diagnosis['confidence_score']:.2%}")

            if result['rare_diseases_considered']:
                print(f"\n=== Rare Diseases Considered ===")
                for diagnosis in result['rare_diseases_considered']:
                    print(f"- {diagnosis['condition_name']} ({diagnosis['confidence_score']:.2%})")

        else:
            print(f"Error: {response.text}")


async def main():
    """Run all tests"""
    try:
        await test_health_check()
        await test_stats()
        await test_diagnostic_analysis()
        await test_rare_disease_case()
    except httpx.ConnectError:
        print("\nError: Could not connect to API server.")
        print("Make sure the server is running: python -m src.main")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
