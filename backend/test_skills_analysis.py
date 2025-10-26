#!/usr/bin/env python3
"""
Test script for the enhanced skills analysis functionality
Demonstrates how to extract and analyze skills from job postings.
"""

import asyncio
import json
from pathlib import Path

# Add the app directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.crawl4ai_service import Crawl4AIService

async def test_skills_extraction():
    """Test the skills extraction and analysis functionality"""
    print("🔍 Testing Skills Extraction and Analysis")
    print("=" * 60)
    
    service = BrightDataMCPService()
    
    # Test 1: Basic skills analysis
    print("\n📚 Test 1: Basic Skills Analysis")
    print("-" * 40)
    
    skills_data = await service.scrape_jobs_with_skills_analysis(
        keywords="software engineer",
        location="San Francisco",
        max_results=5
    )
    
    if skills_data['success']:
        print(f"✅ Successfully analyzed {skills_data['total_jobs_analyzed']} job postings")
        print(f"✅ Extracted {len(skills_data['skills_analysis'])} unique skills")
        print(f"✅ Top 10 skills: {skills_data['top_skills'][:10]}")
        
        # Show detailed insights
        insights = service.get_skills_insights(skills_data['skills_analysis'])
        print(f"\n📊 Detailed Insights:")
        print(f"   - Total skills found: {insights['total_skills_found']}")
        print(f"   - Total skill mentions: {insights['total_skill_mentions']}")
        print(f"   - Most demanded skill: {insights['most_demanded_skill']}")
        print(f"   - Skills diversity score: {insights['skills_diversity_score']:.2f}")
        
        # Show skill categories
        print(f"\n🏷️  Skill Categories:")
        for category, skills in insights['skill_categories'].items():
            if skills:
                skill_names = [skill[0] for skill in skills[:3]]
                print(f"   - {category.replace('_', ' ').title()}: {skill_names}")
        
        # Show requirements analysis
        print(f"\n📋 Requirements Analysis:")
        req_analysis = skills_data['requirements_analysis']
        if req_analysis:
            top_reqs = list(req_analysis.items())[:5]
            print(f"   - Top requirements: {[req[0] for req in top_reqs]}")
        
        # Show qualifications analysis
        print(f"\n🎓 Qualifications Analysis:")
        qual_analysis = skills_data['qualifications_analysis']
        if qual_analysis:
            top_quals = list(qual_analysis.items())[:5]
            print(f"   - Top qualifications: {[qual[0] for qual in top_quals]}")
        
    else:
        print(f"❌ Skills analysis failed: {skills_data['error']}")
        return None
    
    return skills_data

async def test_different_job_types():
    """Test skills analysis for different job types"""
    print("\n\n🎯 Testing Different Job Types")
    print("=" * 60)
    
    service = BrightDataMCPService()
    
    job_types = [
        ("data scientist", "San Francisco"),
        ("frontend developer", "New York"),
        ("devops engineer", "Seattle"),
        ("mobile developer", "Austin")
    ]
    
    all_results = {}
    
    for job_type, location in job_types:
        print(f"\n🔍 Analyzing {job_type} jobs in {location}...")
        
        result = await service.scrape_jobs_with_skills_analysis(
            keywords=job_type,
            location=location,
            max_results=3
        )
        
        if result['success']:
            insights = service.get_skills_insights(result['skills_analysis'])
            all_results[job_type] = {
                'top_skills': result['top_skills'][:5],
                'total_skills': insights['total_skills_found'],
                'most_demanded': insights['most_demanded_skill']
            }
            print(f"   ✅ {insights['total_skills_found']} skills found")
            print(f"   🏆 Most demanded: {insights['most_demanded_skill']}")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Compare job types
    print(f"\n📊 Job Type Comparison:")
    for job_type, data in all_results.items():
        print(f"   - {job_type.title()}: {data['most_demanded']} (most demanded)")
    
    return all_results

async def test_skills_from_descriptions():
    """Test skills extraction from individual job descriptions"""
    print("\n\n📝 Testing Skills Extraction from Descriptions")
    print("=" * 60)
    
    service = BrightDataMCPService()
    
    # Sample job descriptions
    sample_descriptions = [
        """
        We are looking for a Senior Python Developer with experience in Django, Flask, and FastAPI.
        Must have knowledge of PostgreSQL, Redis, and AWS services like EC2 and S3.
        Experience with Docker, Kubernetes, and CI/CD pipelines is required.
        Knowledge of React.js and JavaScript is a plus.
        """,
        """
        Join our team as a Full Stack Developer. You'll work with JavaScript, TypeScript, Node.js,
        React, Vue.js, and Angular. Backend experience with Express.js and MongoDB is required.
        We use AWS, Docker, and Jenkins for deployment. Experience with GraphQL and REST APIs.
        """,
        """
        Data Scientist position requiring Python, R, pandas, numpy, scikit-learn, and TensorFlow.
        Experience with Jupyter notebooks, matplotlib, and seaborn for visualization.
        Knowledge of SQL databases and cloud platforms like AWS or GCP.
        Machine learning and deep learning experience preferred.
        """
    ]
    
    print("🔍 Extracting skills from sample descriptions...")
    
    for i, description in enumerate(sample_descriptions, 1):
        skills = service._extract_skills_from_description(description)
        print(f"\n   Description {i}:")
        print(f"   - Skills found: {len(skills)}")
        print(f"   - Skills: {skills[:10]}")  # Show first 10 skills
    
    return True

async def generate_curl_commands():
    """Generate curl commands for testing the new skills analysis API"""
    print("\n\n🌐 Curl Commands for Skills Analysis API")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    print("📝 Note: These endpoints require authentication.")
    print("   You'll need to get a JWT token first from the auth endpoint.")
    print()
    
    print("1. Get Authentication Token:")
    print(f"curl -X POST \"{base_url}/auth/login\" \\")
    print("  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print("  -d \"username=your_email&password=your_password\"")
    print()
    
    print("2. Test Skills Analysis (NEW ENDPOINT):")
    print(f"curl -X POST \"{base_url}/job-analysis/scrape-jobs-with-skills\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"keywords\": \"software engineer\", \"location\": \"San Francisco\", \"max_results\": 10}'")
    print()
    
    print("3. Test Skills Analysis for Data Scientists:")
    print(f"curl -X POST \"{base_url}/job-analysis/scrape-jobs-with-skills\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"keywords\": \"data scientist\", \"location\": \"New York\", \"max_results\": 15}'")
    print()
    
    print("4. Test Skills Analysis for Frontend Developers:")
    print(f"curl -X POST \"{base_url}/job-analysis/scrape-jobs-with-skills\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"keywords\": \"frontend developer\", \"location\": \"Seattle\", \"max_results\": 20}'")
    print()
    
    print("💡 The response will include:")
    print("   - Detailed job information")
    print("   - Skills analysis with frequency counts")
    print("   - Requirements analysis")
    print("   - Qualifications analysis")
    print("   - Skills insights with categories")
    print("   - Top skills ranking")

async def save_test_results(results):
    """Save test results to file"""
    try:
        # Create exports directory
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        # Save results
        results_file = exports_dir / "skills_analysis_test_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Test results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Error saving test results: {e}")

async def main():
    """Main test function"""
    print("🚀 Testing Enhanced Skills Analysis")
    print("=" * 60)
    
    results = {
        "test_timestamp": "2024-01-01T00:00:00Z",
        "tests": {}
    }
    
    try:
        # Test 1: Basic skills analysis
        print("\n" + "="*60)
        skills_data = await test_skills_extraction()
        if skills_data:
            results["tests"]["basic_skills_analysis"] = {
                "success": True,
                "jobs_analyzed": skills_data['total_jobs_analyzed'],
                "skills_found": len(skills_data['skills_analysis']),
                "top_skills": skills_data['top_skills'][:10]
            }
        
        # Test 2: Different job types
        print("\n" + "="*60)
        job_type_results = await test_different_job_types()
        results["tests"]["job_type_analysis"] = job_type_results
        
        # Test 3: Skills from descriptions
        print("\n" + "="*60)
        description_test = await test_skills_from_descriptions()
        results["tests"]["description_extraction"] = {"success": description_test}
        
        # Generate curl commands
        print("\n" + "="*60)
        await generate_curl_commands()
        
        # Save results
        await save_test_results(results)
        
        print("\n" + "="*60)
        print("✅ Skills Analysis Testing Complete!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Skills extraction from job descriptions")
        print("   ✅ Skills frequency analysis")
        print("   ✅ Skills categorization (programming, frameworks, databases, etc.)")
        print("   ✅ Requirements and qualifications analysis")
        print("   ✅ Skills insights and diversity scoring")
        print("   ✅ Support for multiple job types")
        print("\n🎯 Next Steps:")
        print("   1. Test the new API endpoint with curl commands")
        print("   2. Integrate skills analysis into your frontend")
        print("   3. Use MCP commands in Cursor for real LinkedIn data")
        print("   4. Customize skill categories for your specific needs")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        await save_test_results(results)

if __name__ == "__main__":
    asyncio.run(main())
