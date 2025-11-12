"""
Test the AI reasoning assistant features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import asyncio
from pprint import pprint

API_BASE_URL = "http://localhost:8000/api/v1"


async def test_enhanced_analysis():
    """Test enhanced analysis with AI assistant"""
    print("\n" + "="*80)
    print("🤖 TESTING ENHANCED AI ANALYSIS")
    print("="*80)

    # Sample patient case
    patient_case = {
        "case_id": "test_ai_001",
        "age": 35,
        "sex": "female",
        "chief_complaint": "Persistent fatigue and unexplained weight gain",
        "symptoms": [
            {
                "description": "Extreme fatigue lasting 2 months",
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
            }
        ],
        "family_history": ["thyroid disease in mother"]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/analyze/enhanced",
            json=patient_case,
            params={
                "include_explanation": True,
                "include_questions": True,
                "include_report": False
            }
        )

        if response.status_code == 200:
            result = response.json()

            # Display diagnostic result
            diagnostic = result["diagnostic_result"]
            print(f"\n📊 DIAGNOSTIC RESULT")
            print(f"   Confidence: {diagnostic['overall_confidence']:.1%}")
            print(f"   Review Tier: {diagnostic['review_tier']}")

            if diagnostic['differential_diagnoses']:
                print(f"\n🎯 TOP DIAGNOSIS")
                top = diagnostic['differential_diagnoses'][0]
                print(f"   {top['condition_name']}")
                print(f"   Confidence: {top['confidence_score']:.1%}")
                print(f"   Tests: {', '.join(top['recommended_next_steps'][:3])}")

            # Display AI enhancements
            if "ai_enhancements" in result:
                enhancements = result["ai_enhancements"]

                if "detailed_explanation" in enhancements:
                    print(f"\n🗣️  AI EXPLANATION")
                    print("   " + "-"*76)
                    explanation = enhancements["detailed_explanation"]
                    # Word wrap
                    for line in explanation.split('\n'):
                        if line.strip():
                            words = line.split()
                            current_line = "   "
                            for word in words:
                                if len(current_line) + len(word) + 1 <= 80:
                                    current_line += word + " "
                                else:
                                    print(current_line)
                                    current_line = "   " + word + " "
                            if current_line.strip():
                                print(current_line)
                    print("   " + "-"*76)

                if "follow_up_questions" in enhancements:
                    print(f"\n❓ FOLLOW-UP QUESTIONS TO ASK PATIENT")
                    print("   " + "-"*76)
                    for i, question in enumerate(enhancements["follow_up_questions"], 1):
                        print(f"   {i}. {question}")
                    print("   " + "-"*76)

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


async def test_simple_explanation():
    """Test converting medical jargon to simple terms"""
    print("\n" + "="*80)
    print("🎓 TESTING SIMPLE EXPLANATIONS")
    print("="*80)

    technical_text = """Hypothyroidism is characterized by insufficient production of thyroid hormones
    (T3 and T4) by the thyroid gland, resulting in decreased metabolic rate. This manifests clinically
    as fatigue, weight gain, cold intolerance, and bradycardia. Diagnosis is confirmed via elevated
    TSH and decreased free T4 levels. Treatment involves levothyroxine replacement therapy."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/explain",
            params={
                "condition_name": "Hypothyroidism",
                "technical_explanation": technical_text
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n📚 MEDICAL TERM: {result['condition']}")
            print(f"   Reading Level: {result['reading_level']}")
            print(f"\n   PATIENT-FRIENDLY EXPLANATION:")
            print("   " + "-"*76)
            explanation = result["simple_explanation"]
            for line in explanation.split('\n'):
                if line.strip():
                    words = line.split()
                    current_line = "   "
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 80:
                            current_line += word + " "
                        else:
                            print(current_line)
                            current_line = "   " + word + " "
                    if current_line.strip():
                        print(current_line)
            print("   " + "-"*76)
        else:
            print(f"❌ Error: {response.status_code}")


async def test_treatment_recommendations():
    """Test AI treatment recommendations"""
    print("\n" + "="*80)
    print("💊 TESTING TREATMENT RECOMMENDATIONS")
    print("="*80)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/treatment-recommendations",
            params={
                "case_id": "test_001",
                "diagnosis_name": "Hypothyroidism",
                "patient_age": 35,
                "patient_sex": "female",
                "confidence_score": 0.88
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n🏥 DIAGNOSIS: {result['diagnosis']}")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"\n   RECOMMENDATIONS:")
            print("   " + "-"*76)

            recommendations = result["recommendations"]
            for line in recommendations.split('\n'):
                if line.strip():
                    print(f"   {line}")

            print("   " + "-"*76)
            print(f"\n   ⚠️  {result['disclaimer']}")
        else:
            print(f"❌ Error: {response.status_code}")


async def test_stats():
    """Test system stats with AI features"""
    print("\n" + "="*80)
    print("📈 SYSTEM STATS")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/stats")

        if response.status_code == 200:
            stats = response.json()
            print(f"\n   Status: {stats['status']}")
            print(f"   AI Assistant: {stats.get('ai_assistant', 'unknown')}")
            print(f"\n   Enabled Features:")
            for feature, enabled in stats.get('features', {}).items():
                status = "✅" if enabled else "❌"
                print(f"   {status} {feature.replace('_', ' ').title()}")
        else:
            print(f"❌ Error: {response.status_code}")


async def main():
    """Run all AI tests"""
    print("\n" + "="*80)
    print("🚀 AI REASONING ASSISTANT TEST SUITE")
    print("="*80)
    print("\nNOTE: These tests require OpenAI API key or will use mock responses")
    print("Set OPENAI_API_KEY in .env to use real AI responses\n")

    try:
        await test_stats()
        await test_enhanced_analysis()
        await test_simple_explanation()
        await test_treatment_recommendations()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80 + "\n")

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server.")
        print("Make sure the server is running: python -m src.main")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
