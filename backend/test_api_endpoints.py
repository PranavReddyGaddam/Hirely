#!/usr/bin/env python3
"""
Test script for the new job analysis API endpoints
This script tests the services directly and also provides curl commands for API testing.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.crawl4ai_service import Crawl4AIService
from app.services.job_market_analyzer import JobMarketAnalyzer

async def test_services_directly():
    """Test the services directly without API authentication"""
    print("🧪 Testing Services Directly")
    print("=" * 50)
    
    # Test 1: BrightData MCP Service
    print("\n📚 Test 1: BrightData MCP Service")
    print("-" * 30)
    
    service = BrightDataMCPService()
    jobs = await service.scrape_linkedin_jobs(
        keywords="software engineer",
        location="San Francisco",
        max_results=3
    )
    
    if jobs['success']:
        print(f"✅ Scraped {jobs['total_jobs']} jobs")
        for i, job in enumerate(jobs['jobs'][:2], 1):
            print(f"   {i}. {job['title']} at {job['company']}")
    else:
        print(f"❌ Scraping failed: {jobs['error']}")
    
    # Test 2: Enhanced Crawl4AI Service
    print("\n🔧 Test 2: Enhanced Crawl4AI Service")
    print("-" * 30)
    
    async with Crawl4AIService() as crawl_service:
        prep = await crawl_service.scrape_jobs_for_interview_prep(
            job_title="software engineer",
            location="San Francisco",
            max_jobs=3
        )
        
        if prep['success']:
            print(f"✅ Generated {prep['total_questions']} interview questions")
            print(f"   Jobs analyzed: {prep['total_jobs']}")
            print(f"   Top skills: {list(prep['skills_analysis'].keys())[:3]}")
        else:
            print(f"❌ Interview prep failed: {prep['error']}")
    
    # Test 3: Job Market Analyzer
    print("\n🤖 Test 3: Job Market Analyzer")
    print("-" * 30)
    
    analyzer = JobMarketAnalyzer()
    analysis = await analyzer.analyze_job_market(
        keywords="software engineer",
        location="San Francisco",
        analysis_depth="basic"
    )
    
    if analysis['success']:
        print(f"✅ Analysis completed")
        print(f"   Jobs analyzed: {analysis['job_data']['total_jobs_analyzed']}")
        print(f"   AI analysis: {'✅' if analysis['ai_analysis'] else '❌'}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    return jobs, prep, analysis

def generate_curl_commands():
    """Generate curl commands for testing the API endpoints"""
    print("\n\n🌐 Curl Commands for API Testing")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    print("📝 Note: These endpoints require authentication.")
    print("   You'll need to get a JWT token first from the auth endpoint.")
    print()
    
    print("1. Get Authentication Token:")
    print(f"curl -X POST \"{base_url}/auth/login\" \\")
    print("  -H \"Content-Type: application/x-www-form-urlencoded\" \\")
    print("  -d \"username=your_email&password=your_password\"")
    print()
    
    print("2. Test Job Scraping (requires auth token):")
    print(f"curl -X POST \"{base_url}/job-analysis/scrape-jobs\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"keywords\": \"software engineer\", \"location\": \"San Francisco\", \"max_results\": 10}'")
    print()
    
    print("3. Test Job Market Analysis (requires auth token):")
    print(f"curl -X POST \"{base_url}/job-analysis/analyze-job-market\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"keywords\": \"software engineer\", \"location\": \"San Francisco\", \"analysis_depth\": \"comprehensive\"}'")
    print()
    
    print("4. Test Interview Prep Generation (requires auth token):")
    print(f"curl -X POST \"{base_url}/job-analysis/generate-interview-prep\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"job_title\": \"software engineer\", \"location\": \"San Francisco\", \"prep_type\": \"comprehensive\"}'")
    print()
    
    print("5. Test Company Job Scraping (requires auth token):")
    print(f"curl -X POST \"{base_url}/job-analysis/scrape-company-jobs\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"company_name\": \"Google\", \"generate_questions\": true}'")
    print()
    
    print("6. Test Job Market Insights (requires auth token):")
    print(f"curl -X GET \"{base_url}/job-analysis/job-market-insights?keywords=software%20engineer&location=San%20Francisco\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\"")
    print()
    
    print("7. Test Scrape Status (requires auth token):")
    print(f"curl -X GET \"{base_url}/job-analysis/scrape-status\" \\")
    print("  -H \"Authorization: Bearer YOUR_JWT_TOKEN\"")

def test_without_auth():
    """Test endpoints that might work without authentication"""
    print("\n\n🔓 Testing Endpoints Without Authentication")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    print("1. Health Check:")
    print(f"curl -X GET \"{base_url}/health\"")
    print()
    
    print("2. Root Endpoint:")
    print(f"curl -X GET \"{base_url}/\"")
    print()
    
    print("3. API Documentation:")
    print(f"curl -X GET \"{base_url}/docs\"")
    print()
    
    print("4. OpenAPI Schema:")
    print(f"curl -X GET \"{base_url}/api/v1/openapi.json\"")

async def main():
    """Main test function"""
    print("🚀 Testing Job Analysis Integration")
    print("=" * 60)
    
    try:
        # Test services directly
        jobs, prep, analysis = await test_services_directly()
        
        # Generate curl commands
        generate_curl_commands()
        
        # Test without auth
        test_without_auth()
        
        print("\n" + "=" * 60)
        print("✅ Testing Complete!")
        print("\n💡 Next Steps:")
        print("   1. Test the curl commands above with a valid JWT token")
        print("   2. Check the API documentation at http://localhost:8000/docs")
        print("   3. Test the MCP commands in Cursor")
        print("   4. Integrate with your frontend")
        
        # Save test results
        results = {
            "services_test": {
                "brightdata_service": jobs['success'],
                "crawl4ai_service": prep['success'],
                "job_market_analyzer": analysis['success']
            },
            "api_endpoints": [
                "POST /api/v1/job-analysis/scrape-jobs",
                "POST /api/v1/job-analysis/analyze-job-market", 
                "POST /api/v1/job-analysis/generate-interview-prep",
                "POST /api/v1/job-analysis/scrape-company-jobs",
                "GET /api/v1/job-analysis/job-market-insights",
                "GET /api/v1/job-analysis/scrape-status"
            ],
            "server_url": "http://localhost:8000",
            "docs_url": "http://localhost:8000/docs"
        }
        
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Test results saved to: test_results.json")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
